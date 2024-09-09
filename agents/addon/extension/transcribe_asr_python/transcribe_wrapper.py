from typing import Union, List, Tuple, Optional
import asyncio
from time import time

from rte import (
    RteEnv,
    Data
)

from amazon_transcribe.auth import StaticCredentialResolver
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent, TranscriptResultStream, StartStreamTranscriptionEventStream, Item

from .log import logger
from .transcribe_config import TranscribeConfig

DATA_OUT_TEXT_DATA_PROPERTY_LANGUAGE = "language"
DATA_OUT_TEXT_DATA_PROPERTY_TEXT = "text"
DATA_OUT_TEXT_DATA_PROPERTY_TEXT_STABLE = "text_stable"
DATA_OUT_TEXT_DATA_PROPERTY_TEXT_NON_STABLE = "text_non_stable"
DATA_OUT_TEXT_DATA_PROPERTY_IS_FINAL = "is_final"
DATA_OUT_TEXT_DATA_PROPERTY_STREAM_ID = "stream_id"
DATA_OUT_TEXT_DATA_PROPERTY_EOS = "end_of_segment"
DATA_OUT_TEXT_DATA_PROPERTY_TIME = "time" # timestamp, ms
DATA_OUT_TEXT_DATA_PROPERTY_DURATION_MS = "duration_ms"

class AsyncTranscribeWrapper():
    def __init__(self, config: TranscribeConfig, queue: asyncio.Queue, rte:RteEnv, loop: asyncio.BaseEventLoop):
        self.queue = queue
        self.rte = rte
        self.stopped = False
        self.config = config
        self.loop = loop
        self.is_first_frame = True

        if config.access_key and config.secret_key:
            logger.info(f"init trascribe client with access key: {config.access_key}")
            self.transcribe_client = TranscribeStreamingClient(
                region=config.region,
                credential_resolver=StaticCredentialResolver(
                    access_key_id=config.access_key,
                    secret_access_key=config.secret_key
                )
            )
        else:
            logger.info(f"init trascribe client without access key, using default credentials provider chain.")

            self.transcribe_client = TranscribeStreamingClient(
                region=config.region
            )

        asyncio.set_event_loop(self.loop)
        self.reset_stream()

    def set_user_id(self, user_id:str="0", remote_user_id:str="0"):
        logger.info(f"set_user_id: {user_id}, {remote_user_id}")
        self.user_id = user_id
        self.remote_user_id = remote_user_id

    def reset_stream(self):
        self.stream = None
        self.handler = None
        self.event_handler_task = None
        self.is_first_frame = True

    async def cleanup(self):
        if self.stream:
            await self.stream.input_stream.end_stream()
            logger.info("cleanup: stream ended.")

        if self.event_handler_task:
            await self.event_handler_task
            logger.info("cleanup: event handler ended.")

        self.reset_stream()

    async def create_stream(self) -> bool:
        try:
            self.stream = await self.get_transcribe_stream()
            self.handler = TranscribeEventHandler(self.stream.output_stream, self.rte, self.config)
            self.handler.set_user_id(self.user_id, self.remote_user_id)
            self.event_handler_task = asyncio.create_task(self.handler.handle_events())
        except Exception as e:
            logger.exception(e)
            return False

        return True

    async def send_frame(self) -> None:
        self.is_first_frame = True

        while not self.stopped:
            try:
                pcm_frame = await asyncio.wait_for(self.queue.get(), timeout=10.0)

                if pcm_frame is None:
                    logger.warning("send_frame: exit due to None value got.")
                    return

                frame_buf = pcm_frame.get_buf()
                if not frame_buf:
                    logger.warning("send_frame: empty pcm_frame detected.")
                    continue

                if not self.stream:
                    logger.info("lazy init stream.")
                    if not await self.create_stream():
                        continue

                if self.is_first_frame:
                    self.is_first_frame = False
                    self.handler.set_first_frame_time()

                await self.stream.input_stream.send_audio_event(audio_chunk=frame_buf)
                self.queue.task_done()
            except asyncio.TimeoutError:
                if self.stream:
                    await self.cleanup()
                    logger.debug("send_frame: no data for 10s, will close current stream and create a new one when receving new frame.")
                else:
                    logger.debug("send_frame: waiting for pcm frame.")
            except IOError as e:
                logger.exception(f"Error in send_frame: {e}")
            except Exception as e:
                logger.exception(f"Error in send_frame: {e}")
                raise e

        logger.info("send_frame: exit due to self.stopped == True")

    async def transcribe_loop(self) -> None:
        try:
            await self.send_frame()
        except Exception as e:
            logger.exception(e)
        finally:
            await self.cleanup()

    async def get_transcribe_stream(self) -> StartStreamTranscriptionEventStream:
        stream = await self.transcribe_client.start_stream_transcription(
            language_code=self.config.lang_code,
            media_sample_rate_hz=self.config.sample_rate,
            media_encoding=self.config.media_encoding,
            enable_partial_results_stabilization = self.config.enable_partial_results_stabilization
        )
        return stream

    def run(self) -> None:
        self.loop.run_until_complete(self.transcribe_loop())
        self.loop.close()
        logger.info("async_transcribe_wrapper: thread completed.")

    def stop(self) -> None:
        self.stopped = True


class TranscribeEventHandler(TranscriptResultStreamHandler):
    def __init__(self, transcript_result_stream: TranscriptResultStream, rte: RteEnv, transcribe_config: TranscribeConfig):
        super().__init__(transcript_result_stream)
        self.rte = rte
        self.transcribe_config = transcribe_config

        self.user_id = 0
        self.remote_user_id = 0

        # the timestamp(us) of first pcm frame
        self.first_frame_time = 0

    def set_first_frame_time(self, ts: Optional[int] = None):
        if ts:
            self.first_frame_time = ts
        else:
            self.first_frame_time = int(time() * 1000_000)

    def split_items(self, text_result: str, items: List[Item]) -> Tuple[str, str]:
        stable_str, non_stable_str = "", ""

        idx = 0
        full_len = len(text_result)

        for item in items:
            content = item.content
            idx += len(content)

            while idx < full_len and text_result[idx] == ' ':
                content += ' '
                idx += 1

            if item.stable:
                stable_str += content
            else:
                non_stable_str += content

        return stable_str, non_stable_str

    def get_abs_start_time(self, segment_start_time: float):
        """get current segment's absolute start time timestamp(ms)"""
        return self.first_frame_time + int(segment_start_time * 1000)

    async def handle_transcript_event(self, transcript_event: TranscriptEvent) -> None:
        results = transcript_event.transcript.results
        text_result = ""
        is_final, end_of_segment = True, True

        if not results:
            return

        if len(results) > 1:
            logger.warning(f"got more than one result, only handle the first")

        #  only handle the first result
        result = results[0]

        if result.is_partial:
            is_final = False
            end_of_segment = False

        for alt in result.alternatives:
            text_result += alt.transcript

        if not text_result:
            return

        if self.transcribe_config.enable_partial_results_stabilization:
            stable_str, non_stable_str = self.split_items(text_result, result.alternatives[0].items)
        else:
            stable_str, non_stable_str = '', ''

        logger.info(f"got transcript: [{text_result}], is_final: [{is_final}]")

        self.create_and_send_data(
            language=self.transcribe_config.lang_code,
            text_result=text_result,
            text_stable=stable_str,
            text_non_stable=non_stable_str,
            is_final=is_final,
            end_of_segment=end_of_segment,
            start_time=self.get_abs_start_time(result.start_time),
            duration_ms=int((result.end_time - result.start_time) * 1000)
        )

    def set_user_id(self, user_id:str="0", remote_user_id:str="0"):
        self.user_id = int(user_id)
        self.remote_user_id = int(remote_user_id)

    def create_and_send_data(self, language: str, text_result: str, text_stable: str, text_non_stable: str,
                             is_final: bool, end_of_segment: bool, start_time: int, duration_ms: int):
        rte_text_data = Data.create("text_data")
        try:
            rte_text_data.set_property_string(DATA_OUT_TEXT_DATA_PROPERTY_LANGUAGE, language)
            rte_text_data.set_property_int(DATA_OUT_TEXT_DATA_PROPERTY_STREAM_ID, self.remote_user_id)
            rte_text_data.set_property_string(DATA_OUT_TEXT_DATA_PROPERTY_TEXT, text_result)
            rte_text_data.set_property_string(DATA_OUT_TEXT_DATA_PROPERTY_TEXT_STABLE, text_stable)
            rte_text_data.set_property_string(DATA_OUT_TEXT_DATA_PROPERTY_TEXT_NON_STABLE, text_non_stable)
            rte_text_data.set_property_bool(DATA_OUT_TEXT_DATA_PROPERTY_IS_FINAL, is_final)
            rte_text_data.set_property_bool(DATA_OUT_TEXT_DATA_PROPERTY_EOS, end_of_segment)
            rte_text_data.set_property_int(DATA_OUT_TEXT_DATA_PROPERTY_TIME, start_time)
            rte_text_data.set_property_int(DATA_OUT_TEXT_DATA_PROPERTY_DURATION_MS, duration_ms)

            self.rte.send_data(rte_text_data)
        except Exception as e:
            logger.error(e)
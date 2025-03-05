import json
from threading import Thread
from time import time
from rte import (
    Extension,
    RteEnv,
    Cmd,
    Data,
    StatusCode,
    CmdResult,
)
from .dify_llm import DifyLLM, DifyLLMConfig
from .log import logger
from .property import *

def get_current_time():
    """Get current time in milliseconds"""
    return int(time() * 1000)

def parse_sentence(sentence, content):
    """Parse a sentence from content and return the sentence and remaining content"""
    remain = ""
    found_punc = False

    for char in content:
        if not found_punc:
            sentence += char
        else:
            remain += char

        if not found_punc and char in PUNCUTATIONS:
            found_punc = True

    return sentence, remain, found_punc

class DifyExtension(Extension):
    memory = []
    outdate_ts = 0
    dify_llm = None
    pending_inputs = []  # Store incoming data
    is_processing = False  # Flag to track if a dify request is being processed

    def on_start(self, rte: RteEnv) -> None:
        logger.info("DifyExtension on_start")
        # Prepare configuration
        dify_config = DifyLLMConfig.default_config()

        for optional_str_param in [PROPERTY_BASE_URL, PROPERTY_API_KEY, PROPERTY_USER_ID, 
                                 PROPERTY_GREETING, PROPERTY_FAILURE_INFO]:
            try:
                value = rte.get_property_string(optional_str_param).strip()
                if value:
                    setattr(dify_config, optional_str_param, value)
            except Exception as err:
                logger.debug(f"GetProperty optional {optional_str_param} failed, err: {err}. Using default value: {getattr(dify_config, optional_str_param)}")

        try:
            max_history = rte.get_property_int(PROPERTY_MAX_HISTORY)
            if max_history > 0:
                dify_config.max_history = max_history
        except Exception as err:
            logger.debug(f"GetProperty optional {PROPERTY_MAX_HISTORY} failed, err: {err}. Using default value: {dify_config.max_history}")

        dify_config.validate()
        self.rte = rte

        # Create DifyLLM instance
        try:
            self.dify_llm = DifyLLM(dify_config)
            logger.info(f"Created DifyLLM instance with config: {dify_config}")
        except Exception as err:
            logger.exception(f"Failed to create DifyLLM instance: {err}")

        # Send greeting if available
        if dify_config.greeting:
            try:
                self._send_text(dify_config.greeting, True)
                logger.info(f"Greeting [{dify_config.greeting}] sent")
            except Exception as err:
                logger.info(f"Failed to send greeting [{dify_config.greeting}], err: {err}")

        rte.on_start_done()

    def on_stop(self, rte: RteEnv) -> None:
        logger.info("DifyExtension on_stop")
        rte.on_stop_done()

    def on_cmd(self, rte: RteEnv, cmd: Cmd) -> None:
        logger.info("DifyExtension on_cmd")
        cmd_name = cmd.get_name()
        logger.info(f"DifyExtension on_cmd name: {cmd_name}")

        if cmd_name == CMD_IN_FLUSH:
            self.outdate_ts = get_current_time()
            cmd_out = Cmd.create(CMD_OUT_FLUSH)
            rte.send_cmd(cmd_out, None)
            logger.info("DifyExtension on_cmd sent flush")
        else:
            logger.info(f"DifyExtension on_cmd unknown cmd: {cmd_name}")
            cmd_result = CmdResult.create(StatusCode.ERROR)
            cmd_result.set_property_string("detail", "unknown cmd")
            rte.return_result(cmd_result, cmd)
            return

        cmd_result = CmdResult.create(StatusCode.OK)
        cmd_result.set_property_string("detail", "success")
        rte.return_result(cmd_result, cmd)


    def on_data(self, rte: RteEnv, data: Data) -> None:
        logger.info("DifyExtension on_data")

        is_final = False
        input_text = ""
        try:
            is_final = data.get_property_bool(DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL)
        except Exception as err:
            logger.info(
                f"GetProperty optional {DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL} failed, err: {err}"
            )

        try:
            input_text = data.get_property_string(DATA_IN_TEXT_DATA_PROPERTY_TEXT)
        except Exception as err:
            logger.info(
                f"GetProperty optional {DATA_IN_TEXT_DATA_PROPERTY_TEXT} failed, err: {err}"
            )

        if not is_final:
            logger.info("ignore non-final input")
            return
        if not input_text:
            logger.info("ignore empty text")
            return

        # Store input in pending_inputs array
        self.pending_inputs.append(input_text)
        logger.info(f"Stored input text: [{input_text}] in pending_inputs")

        # Only process if no ongoing dify request
        if not self.is_processing:
            self._process_pending_inputs()

    def _process_pending_inputs(self):
        if not self.pending_inputs:
            return

        self.is_processing = True
        combined_input = "\n".join(self.pending_inputs)
        self.pending_inputs = []  # Clear the pending inputs

        # Prepare memory
        while len(self.memory):
            if len(self.memory) > self.dify_llm.config.max_history:
                logger.debug(f"Pop out first message due to memory length limit: {self.memory[0]}")
                self.memory.pop(0)
            elif self.memory[0]["role"] == "assistant":
                logger.debug(f"Pop out first message as messages cannot start with assistant: {self.memory[0]}")
                self.memory.pop(0)
            else:
                break

        if len(self.memory) and self.memory[-1]["role"] == "user":
            logger.debug("Appending input to last user message")
            self.memory[-1]["content"].append({"text": combined_input})
        else:
            self.memory.append({"role": "user", "content": [{"text": combined_input}]})

        def chat_stream_worker(start_time, input_text, memory):
            try:
                logger.info(f"Starting chat stream for input: [{input_text}], memory: {memory}")
                
                # Get chat stream from Dify
                response = self.dify_llm.get_chat_stream(memory)
                if response is None:
                    logger.error(f"Failed to get chat stream for input: [{input_text}]")
                    try:
                        self._send_text(self.dify_llm.config.failure_info, True)
                    except Exception as err:
                        logger.error(f"Failed to send failure message: {err}")
                    return
                
                sentence = ""
                full_content = ""
                first_sentence_sent = False
                
                # Process the streaming response
                for line in response.iter_lines():
                    # Check for interruption
                    if (start_time + 100_000) < self.outdate_ts:
                        logger.info(f"Chat stream interrupted, startTs: {start_time}, outdateTs: {self.outdate_ts}")
                        break

                    if not line:
                        continue

                    line_text = line.decode("utf-8").strip()
                    if not line_text.startswith("data:"):
                        continue

                    content = line_text[5:].strip()
                    if content == "[DONE]":
                        break

                    try:
                        message_data = json.loads(content)

                        # Store conversation_id if received
                        if not self.dify_llm.conversation_id and message_data.get("conversation_id"):
                            self.dify_llm.conversation_id = message_data["conversation_id"]
                            logger.info(f"Stored conversation_id: {self.dify_llm.conversation_id}")

                        event_type = message_data.get("event")

                        if event_type in ["message", "agent_message"]:
                            content = message_data.get("answer", "")
                            full_content += content
                            
                            while True:
                                sentence, content, sentence_is_final = parse_sentence(sentence, content)
                                if not sentence or not sentence_is_final:
                                    break

                                try:
                                    self._send_text(sentence, False)
                                    logger.info(f"Sent sentence: [{sentence}]")
                                except Exception as err:
                                    logger.error(f"Failed to send sentence [{sentence}]: {err}")
                                    break

                                sentence = ""
                                if not first_sentence_sent:
                                    first_sentence_sent = True
                                    logger.info(f"First sentence sent, latency: {get_current_time() - start_time}ms")

                        elif event_type == "message_end":
                            metadata = message_data.get("metadata", {})
                            logger.info(f"metadata: {metadata}")

                        elif event_type == "error":
                            error_message = message_data.get("message", "Unknown error")
                            logger.error(f"Error in chat stream: {error_message}")
                            try:
                                self._send_text(error_message, True)
                            except Exception as err:
                                logger.error(f"Failed to send error message: {err}")
                            return

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        continue

                # Store response in memory if not empty
                if full_content.strip():
                    if memory and memory[-1]["role"] == "assistant":
                        memory[-1]["content"] += full_content
                    else:
                        memory.append({"role": "assistant", "content": full_content})

                # Send final segment
                try:
                    self._send_text(sentence, True)
                    logger.info(f"Sent final segment with remaining sentence: [{sentence}]")
                except Exception as err:
                    logger.error(f"Failed to send final segment: {err}")

                # Reset processing flag and process any pending inputs
                self.is_processing = False
                if self.pending_inputs:
                    self._process_pending_inputs()

            except Exception as e:
                logger.error(f"Error in chat stream worker: {str(e)}")
                try:
                    self._send_text(self.dify_llm.config.failure_info, True)
                except Exception as err:
                    logger.error(f"Failed to send failure message: {err}")
                
                # Reset processing flag even on error
                self.is_processing = False
                if self.pending_inputs:
                    self._process_pending_inputs()

        # Start thread for chat stream processing
        start_time = get_current_time()
        thread = Thread(target=chat_stream_worker, args=(start_time, combined_input, self.memory))
        thread.start()
        logger.info("DifyExtension on_data end")

    def _send_text(self, text: str, end_of_segment: bool):
        output_data = Data.create("text_data")
        output_data.set_property_string(DATA_OUT_TEXT_DATA_PROPERTY_TEXT, text)
        output_data.set_property_bool(DATA_OUT_TEXT_DATA_PROPERTY_END_OF_SEGMENT, end_of_segment)
        self.rte.send_data(output_data)

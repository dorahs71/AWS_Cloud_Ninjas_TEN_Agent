from rte import (
    Extension,
    RteEnv,
    PcmFrame,
    PcmFrameDataFmt,
)

import asyncio
import threading
import time
import numpy as np
import librosa
import queue
import collections

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks

from .log import logger

PROPERTY_SAMPLE_RATE_IN  = 'sample_rate_in'  # Optional
PROPERTY_SAMPLE_RATE_OUT = 'sample_rate_out'  # Optional

MODEL_SAMPLE_RATE = 48000
BATCH_SIZE = 4  # Process 4 frames at once (40ms)

class AudioDenoiseExtension(Extension):
    # Default sample rates
    sample_rate_in = 16000
    sample_rate_out = 16000

    def __init__(self, name: str):
        super().__init__(name)

        # Thread synchronization and control
        self.stopped = False
        self.thread = None
        self.loop = None
        self._lock = threading.RLock()  # For thread-safe access to shared resources
        
        # Audio processing resources
        self.denoiser = None
        
        # Initialize the denoising model
        self.__init_denoise_model()
        
        # Thread-safe queue for handling multiple frames
        # Capacity: ~30 seconds of audio (3000 frames at 10ms each)
        self.frame_queue = queue.Queue(maxsize=3000)
        
        # Buffer to collect frames for batch processing
        # Note: This is accessed only from the processing thread, so no lock needed
        self.frame_buffer = collections.deque(maxlen=BATCH_SIZE)
        
        logger.info("AudioDenoiseExtension initialized")

        self.input_file = open('/tmp/input_16k.pcm', 'wb')
        self.output_file = open('/tmp/output_48k.pcm', 'wb')

    def on_start(self, rte: RteEnv) -> None:
        """
        Initialize and start the audio denoising extension.
        Called by the RTE framework when the extension is started.
        
        Args:
            rte: The RTE environment instance
        """
        logger.info("AudioDenoiseExtension on_start")
        
        # Load configuration from properties
        self._load_configuration(rte)
        
        # Ensure we're not already running
        with self._lock:
            if self.thread and self.thread.is_alive():
                logger.warning("Audio denoising thread already running, not starting another")
                rte.on_start_done()
                return
                
            # Reset state
            self.stopped = False
            
            # Start the processing thread
            logger.info("Starting audio denoising thread")
            self.thread = threading.Thread(
                target=self.process_audio, 
                args=[rte],
                name="AudioDenoiseThread"
            )
            self.thread.daemon = True  # Allow the thread to exit when the main process exits
            self.thread.start()
            
        rte.on_start_done()
        
    def _load_configuration(self, rte: RteEnv) -> None:
        """
        Load configuration from RTE properties.
        
        Args:
            rte: The RTE environment instance
        """
        for optional_param in [PROPERTY_SAMPLE_RATE_IN, PROPERTY_SAMPLE_RATE_OUT]:
            try:
                value = rte.get_property_string(optional_param).strip()
                if value:
                    with self._lock:
                        self.__setattr__(optional_param, int(value))
                    logger.info(f"Set {optional_param} to {int(value)}")
            except Exception as err:
                logger.debug(f"GetProperty optional {optional_param} failed, err: {err}. Using default value: {self.__getattribute__(optional_param)}")

    def put_pcm_frame(self, pcm_frame: PcmFrame) -> None:
        """
        Add a PCM frame to the processing queue.
        
        Args:
            pcm_frame: The PCM frame to process, or None to signal thread termination
        """
        try:
            # Check if extension is stopped
            if self.stopped and pcm_frame is not None:
                logger.debug("Extension stopped, not accepting new frames")
                return
                
            # Check if frame is None (used as a signal to stop processing)
            if pcm_frame is None:
                logger.debug("Received None frame, signaling thread termination")
                self.frame_queue.put(pcm_frame, block=False)
                return
                
            # Check if frame has valid data
            frame_buf = pcm_frame.get_buf()
            if not frame_buf or len(frame_buf) == 0:
                logger.warning("Skipping empty PCM frame")
                return
            self.input_file.write(frame_buf)

            # Use a thread-safe queue to handle multiple frames
            self.frame_queue.put(pcm_frame, block=False)
        except queue.Full:
            logger.warning("Queue is full, dropping frame")
        except Exception as e:
            logger.exception(f"Exception in put_pcm_frame: {e}")

    def on_pcm_frame(self, rte: RteEnv, pcm_frame: PcmFrame) -> None:
        """
        Handle incoming PCM frames from the RTE framework.
        
        Args:
            rte: The RTE environment instance
            pcm_frame: The PCM frame to process
        """
        self.put_pcm_frame(pcm_frame=pcm_frame)

    def on_stop(self, rte: RteEnv) -> None:
        """
        Stop the audio denoising extension.
        Called by the RTE framework when the extension is stopped.
        
        Args:
            rte: The RTE environment instance
        """
        logger.info("AudioDenoiseExtension on_stop")
        
        with self._lock:
            # Mark as stopped to prevent accepting new frames
            self.stopped = True
            
            # Put an empty frame to stop the processing thread
            try:
                self.put_pcm_frame(None)
            except Exception as e:
                logger.warning(f"Error sending stop signal to processing thread: {e}")
            
            # Wait for the processing thread to finish
            if self.thread and self.thread.is_alive():
                logger.info("Waiting for audio processing thread to finish...")
                self.thread.join(timeout=5.0)
                
                if self.thread.is_alive():
                    logger.warning("Audio processing thread did not exit within timeout")
                else:
                    logger.info("Audio processing thread exited successfully")

            self.input_file.close()
            self.output_file.close()
        rte.on_stop_done()

    def process_audio(self, rte: RteEnv) -> None:
        """
        Main audio processing thread function.
        Processes audio frames from the queue and applies denoising in batches.
        
        Args:
            rte: The RTE environment instance
        """
        logger.info("Audio denoising thread started")
        
        try:
            # Create and set the event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Track total duration for batched frames
            total_batch_duration_ms = 0
            
            # Main processing loop
            while not self.stopped:
                try:
                    # Get a frame from the queue with timeout
                    try:
                        pcm_frame = self.frame_queue.get(timeout=30.0)
                        # Mark task as done to prevent queue from growing indefinitely
                        self.frame_queue.task_done()
                    except queue.Empty:
                        # If we have frames in the buffer but haven't reached BATCH_SIZE,
                        # process them anyway after a timeout to avoid excessive latency
                        if len(self.frame_buffer) > 0:
                            logger.info(f"Processing partial batch of {len(self.frame_buffer)} frames after timeout")
                            self.__process_batch(rte, self.frame_buffer, total_batch_duration_ms)
                            self.frame_buffer.clear()
                            total_batch_duration_ms = 0
                        logger.debug("process_audio: waiting for pcm frame.")
                        continue
                    
                    # Check for termination signal
                    if pcm_frame is None:
                        # Process any remaining frames in the buffer before exiting
                        if len(self.frame_buffer) > 0:
                            logger.info(f"Processing final batch of {len(self.frame_buffer)} frames before exit")
                            self.__process_batch(rte, self.frame_buffer, total_batch_duration_ms)
                        logger.info("Received termination signal, exiting processing loop")
                        break
                    
                    # Get the audio data from the frame
                    frame_buf = pcm_frame.get_buf()
                    if not frame_buf:
                        logger.warning("process_audio: empty pcm_frame detected.")
                        continue
    
                    # Extract frame metadata
                    frame_sample_rate = pcm_frame.get_sample_rate()
                    bytes_per_sample = pcm_frame.get_bytes_per_sample()
                    duration_ms = int(len(frame_buf) / bytes_per_sample / frame_sample_rate * 1000)
                    
                    # Resample if needed
                    if frame_sample_rate != MODEL_SAMPLE_RATE:
                        frame_buf = self.__resample_bytes(frame_buf, frame_sample_rate, MODEL_SAMPLE_RATE)
                        
                        # Skip if resampling resulted in empty buffer
                        if not frame_buf or len(frame_buf) == 0:
                            logger.warning("Skipping frame after failed resampling")
                            continue
                    
                    # Add frame to buffer and update total duration
                    self.frame_buffer.append((pcm_frame, frame_buf, duration_ms))
                    total_batch_duration_ms += duration_ms
                    
                    # Process batch when we have collected BATCH_SIZE frames
                    if len(self.frame_buffer) >= BATCH_SIZE:
                        self.__process_batch(rte, self.frame_buffer, total_batch_duration_ms)
                        self.frame_buffer.clear()
                        total_batch_duration_ms = 0
    
                except Exception as e:
                    logger.exception(f"Error processing audio frame: {e}")
                    # Continue processing next frame despite errors
        
        except Exception as e:
            logger.exception(f"Fatal error in audio processing thread: {e}")
        finally:
            # Clean up resources
            logger.info("Cleaning up audio processing resources")
            
            # Clean up the event loop
            if self.loop and not self.loop.is_closed():
                self.loop.close()
                self.loop = None
                
            logger.info("Audio denoising thread stopped")
        
    def __process_batch(self, rte: RteEnv, frame_batch, total_duration_ms):
        """
        Process a batch of audio frames together.
        
        Args:
            rte: The RTE environment instance
            frame_batch: List of tuples containing (original_frame, processed_buffer, duration_ms)
            total_duration_ms: Total duration of all frames in milliseconds
        """
        if not frame_batch:
            logger.debug("Empty batch received, nothing to process")
            return
            
        try:
            # Concatenate all frame buffers
            all_buffers = b''.join([frame_data[1] for frame_data in frame_batch])
            
            # Check if we have any audio data to process
            if not all_buffers or len(all_buffers) == 0:
                logger.warning("Empty audio buffer after concatenation, skipping batch processing")
                return
                
            # Apply denoising to the concatenated audio
            batch_start_time = time.time()
            result = self.denoiser(all_buffers)
            denoised_pcm = result['output_pcm']
            batch_process_time = (time.time() - batch_start_time)*1000
            
            # Resample output if needed
            if self.sample_rate_out != MODEL_SAMPLE_RATE:
                denoised_pcm = self.__resample_bytes(denoised_pcm, MODEL_SAMPLE_RATE, self.sample_rate_out)
                
                # Check if resampling was successful
                if not denoised_pcm or len(denoised_pcm) == 0:
                    logger.warning("Resampling output resulted in empty buffer, falling back to original frames")
                    self.__send_original_frames(rte, frame_batch)
                    return
            self.output_file.write(denoised_pcm)
            # Create a new PCM frame with the denoised audio
            denoised_frame = self.__get_frame(denoised_pcm, self.sample_rate_out, total_duration_ms)
            
            # Send the denoised frame
            rte.send_pcm_frame(denoised_frame)
            # logger.info(f"Sent denoised batch frame of {total_duration_ms}ms (processed in {batch_process_time:.1f}s)")

        except Exception as e:
            logger.exception(f"Error in batch denoising: {e}")
            # If denoising fails, pass through the original frames
            self.__send_original_frames(rte, frame_batch)
            
    def __send_original_frames(self, rte: RteEnv, frame_batch):
        """
        Send original frames as fallback when denoising fails.
        
        Args:
            rte: The RTE environment instance
            frame_batch: List of tuples containing (original_frame, processed_buffer, duration_ms)
        """
        logger.info("Falling back to original frames")
        for frame_data in frame_batch:
            original_frame = frame_data[0]
            rte.send_pcm_frame(original_frame)

    def __resample_bytes(self, input_bytes:bytes, orig_sr:int, target_sr:int) -> bytes:
        """
        Resample raw PCM bytes from original sample rate to target sample rate
        
        Args:
            input_bytes (bytes): Raw PCM bytes at original sample rate (16-bit, mono)
            orig_sr (int): Original sample rate in Hz (e.g., 48000 for 48kHz)
            target_sr (int): Target sample rate in Hz (e.g., 16000 for 16kHz)
            
        Returns:
            bytes: Resampled PCM bytes at target sample rate (16-bit, mono)
        """
        # Check if input is empty
        if not input_bytes or len(input_bytes) == 0:
            logger.warning(f"Empty input buffer received for resampling from {orig_sr} to {target_sr}")
            return bytes(0)  # Return empty bytes
            
        # Convert bytes to numpy array (assuming 16-bit PCM)
        audio_np = np.frombuffer(input_bytes, dtype=np.int16)
        
        # Check if we have enough samples to resample
        if len(audio_np) == 0:
            logger.warning(f"Zero-length audio array after conversion from bytes")
            return bytes(0)  # Return empty bytes
            
        # Convert to float for librosa (normalize to [-1.0, 1.0])
        audio_float = audio_np.astype(np.float32) / 32768.0
        
        # Resample from original sample rate to target sample rate
        audio_resampled = librosa.resample(audio_float, orig_sr=orig_sr, target_sr=target_sr)
        
        # Convert back to int16
        audio_resampled_int16 = (audio_resampled * 32768.0).astype(np.int16)
        
        # Convert to bytes
        output_bytes = audio_resampled_int16.tobytes()
        
        return output_bytes


    def __get_frame(self, data: bytes, sample_rate:int, duration_ms:int) -> PcmFrame:
        """
        Create a new PCM frame with the given audio data.
        
        Args:
            data: Raw PCM audio data as bytes
            sample_rate: Sample rate in Hz
            duration_ms: Duration of the audio in milliseconds
            
        Returns:
            A new PcmFrame object containing the audio data
        """
        # Calculate frame parameters
        samples = int(sample_rate / 1000 * duration_ms)
        sample_bytes = int(samples * 2)  # 2 bytes per sample (16-bit)
        
        # Create and configure the frame
        f = PcmFrame.create("pcm_frame")
        f.set_sample_rate(sample_rate)
        f.set_bytes_per_sample(2)  # 16-bit audio
        f.set_number_of_channels(1)  # Mono audio
        f.set_data_fmt(PcmFrameDataFmt.INTERLEAVE)
        f.set_samples_per_channel(samples)
        
        # Allocate buffer and copy data
        f.alloc_buf(sample_bytes)
        buff = f.lock_buf()
        
        # Handle potential size mismatch between data and buffer
        data_len = len(data)
        buff_len = len(buff)
        
        # Copy only as much data as the buffer can hold
        copy_len = min(data_len, buff_len)
        
        # Use a loop to copy byte by byte to avoid memoryview structure mismatch
        for i in range(copy_len):
            buff[i] = data[i]
            
        f.unlock_buf(buff)
        
        return f

    def __init_denoise_model(self):
        """
        Initialize the audio denoising model.
        This method is thread-safe and will only initialize the model once.
        """
        with self._lock:
            if self.denoiser:
                logger.debug("Denoising model already initialized")
                return
    
            # Initialize the denoiser
            logger.info("Loading audio denoising model...")
            model_load_start = time.time()
            
            try:
                self.denoiser = pipeline(
                    Tasks.acoustic_noise_suppression,
                    model='iic/speech_dfsmn_ans_psm_48k_causal',
                    stream_mode=True
                )
                
                model_load_time = time.time() - model_load_start
                logger.info(f"Audio denoising model loaded in {model_load_time:.2f} seconds")
                
                # Warmup inference with empty audio to initialize internal state
                logger.debug("Performing warmup inference")
                for i in range(100):
                    self.denoiser(bytes(3840))  # 3840 bytes = 1920 samples at 16-bit
                logger.debug("Warmup inference completed")
            except Exception as e:
                logger.exception(f"Failed to initialize denoising model: {e}")
                raise

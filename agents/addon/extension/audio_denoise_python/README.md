## Audio Denoise Extension

This extension provides real-time audio denoising functionality using the ModelScope acoustic noise suppression model.

### Features

- Streams audio denoising in real-time
- Processes PCM audio frames from Agora RTC
- Outputs denoised PCM frames
- Uses the ModelScope `iic/speech_dfsmn_ans_psm_48k_causal` model

### Implementation Details

The extension receives PCM audio frames from the RTC engine, processes them through the ModelScope denoising pipeline, and outputs the denoised audio frames. The processing is done in a streaming fashion to maintain low latency.
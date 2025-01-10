/**
 *
 * Agora Real Time Engagement
 * Created by Hai Guo in 2024-08.
 * Copyright (c) 2024 Agora IO. All rights reserved.
 *
 */
// An extension written by Go for TTS
package extension

import (
	"fmt"
	"io"
	"log/slog"
	"sync"
	"sync/atomic"
	"time"

	"agora.io/rte/rte"
)

const (
	cmdInFlush                 = "flush"
	cmdOutFlush                = "flush"
	dataInTextDataPropertyText = "text"

	propertyApiKey                   = "api_key"                    // Required
	propertyModelId                  = "model_id"                   // Optional
	propertyOptimizeStreamingLatency = "optimize_streaming_latency" // Optional
	propertyRequestTimeoutSeconds    = "request_timeout_seconds"    // Optional
	propertyBaseUrl                  = "base_url"                   // Optional
)

const (
	textChanMax = 1024
)

var (
	logTag = slog.String("extension", "FISHAUDIO_TTS_EXTENSION")

	outdateTs atomic.Int64
	textChan  chan *message
	wg        sync.WaitGroup
)

type fishAudioTTSExtension struct {
	rte.DefaultExtension
	fishAudioTTS *fishAudioTTS
}

type message struct {
	text       string
	receivedTs int64
}

func newFishAudioTTSExtension(name string) rte.Extension {
	return &fishAudioTTSExtension{}
}

// OnStart will be called when the extension is starting,
// properies can be read here to initialize and start the extension.
// current supported properties:
//   - api_key (required)
//   - model_id
//   - optimize_streaming_latency
//   - request_timeout_seconds
//   - base_url
func (e *fishAudioTTSExtension) OnStart(rteEnv rte.RteEnv) {
	slog.Info("OnStart", logTag)

	// prepare configuration
	fishAudioTTSConfig := defaultFishAudioTTSConfig()

	if apiKey, err := rteEnv.GetPropertyString(propertyApiKey); err != nil {
		slog.Error(fmt.Sprintf("GetProperty required %s failed, err: %v", propertyApiKey, err), logTag)
		return
	} else {
		fishAudioTTSConfig.ApiKey = apiKey
	}

	if modelId, err := rteEnv.GetPropertyString(propertyModelId); err != nil {
		slog.Warn(fmt.Sprintf("GetProperty optional %s failed, err: %v", propertyModelId, err), logTag)
	} else {
		if len(modelId) > 0 {
			fishAudioTTSConfig.ModelId = modelId
		}
	}

	if optimizeStreamingLatency, err := rteEnv.GetPropertyBool(propertyOptimizeStreamingLatency); err != nil {
		slog.Warn(fmt.Sprintf("GetProperty optional %s failed, err: %v", propertyOptimizeStreamingLatency, err), logTag)
	} else {
		fishAudioTTSConfig.OptimizeStreamingLatency = optimizeStreamingLatency
	}

	if requestTimeoutSeconds, err := rteEnv.GetPropertyInt64(propertyRequestTimeoutSeconds); err != nil {
		slog.Warn(fmt.Sprintf("GetProperty optional %s failed, err: %v", propertyRequestTimeoutSeconds, err), logTag)
	} else {
		if requestTimeoutSeconds > 0 {
			fishAudioTTSConfig.RequestTimeoutSeconds = int(requestTimeoutSeconds)
		}
	}

	if baseUrl, err := rteEnv.GetPropertyString(propertyBaseUrl); err != nil {
		slog.Warn(fmt.Sprintf("GetProperty optional %s failed, err: %v", propertyBaseUrl, err), logTag)
	} else {
		if len(baseUrl) > 0 {
			fishAudioTTSConfig.BaseUrl = baseUrl
		}
	}

	// create fishAudioTTS instance
	fishAudioTTS, err := newFishAudioTTS(fishAudioTTSConfig)
	if err != nil {
		slog.Error(fmt.Sprintf("newFishAudioTTS failed, err: %v", err), logTag)
		return
	}

	slog.Info(fmt.Sprintf("newFishAudioTTS succeed with ModelId: %s",
		fishAudioTTSConfig.ModelId), logTag)

	// set fishAudio instance
	e.fishAudioTTS = fishAudioTTS

	// create pcm instance
	pcm := newPcm(defaultPcmConfig())
	pcmFrameSize := pcm.getPcmFrameSize()

	// init chan
	textChan = make(chan *message, textChanMax)

	go func() {
		slog.Info("process textChan", logTag)

		for msg := range textChan {
			if msg.receivedTs < outdateTs.Load() { // Check whether to interrupt
				slog.Info(fmt.Sprintf("textChan interrupt and flushing for input text: [%s], receivedTs: %d, outdateTs: %d",
					msg.text, msg.receivedTs, outdateTs.Load()), logTag)
				continue
			}

			wg.Add(1)
			slog.Info(fmt.Sprintf("textChan text: [%s]", msg.text), logTag)

			r, w := io.Pipe()
			startTime := time.Now()

			go func() {
				defer wg.Done()
				defer w.Close()

				slog.Info(fmt.Sprintf("textToSpeechStream text: [%s]", msg.text), logTag)
				err = e.fishAudioTTS.textToSpeechStream(rteEnv, w, msg.text)
				slog.Info(fmt.Sprintf("textToSpeechStream result: [%v]", err), logTag)
				if err != nil {
					slog.Error(fmt.Sprintf("textToSpeechStream failed, err: %v", err), logTag)
					return
				}
			}()

			slog.Info(fmt.Sprintf("read pcm stream, text:[%s], pcmFrameSize:%d", msg.text, pcmFrameSize), logTag)

			var (
				firstFrameLatency int64
				n                 int
				pcmFrameRead      int
				readBytes         int
				sentFrames        int
			)
			buf := pcm.newBuf()

			// read pcm stream
			for {
				if msg.receivedTs < outdateTs.Load() { // Check whether to interrupt
					slog.Info(fmt.Sprintf("read pcm stream interrupt and flushing for input text: [%s], receivedTs: %d, outdateTs: %d",
						msg.text, msg.receivedTs, outdateTs.Load()), logTag)
					break
				}

				n, err = r.Read(buf[pcmFrameRead:])
				readBytes += n
				pcmFrameRead += n

				if err != nil {
					if err == io.EOF {
						slog.Info("read pcm stream EOF", logTag)
						break
					}

					slog.Error(fmt.Sprintf("read pcm stream failed, err: %v", err), logTag)
					break
				}

				if pcmFrameRead != pcmFrameSize {
					slog.Debug(fmt.Sprintf("the number of bytes read is [%d] inconsistent with pcm frame size", pcmFrameRead), logTag)
					continue
				}

				pcm.send(rteEnv, buf)
				// clear buf
				buf = pcm.newBuf()
				pcmFrameRead = 0
				sentFrames++

				if firstFrameLatency == 0 {
					firstFrameLatency = time.Since(startTime).Milliseconds()
					slog.Info(fmt.Sprintf("first frame available for text: [%s], receivedTs: %d, firstFrameLatency: %dms", msg.text, msg.receivedTs, firstFrameLatency), logTag)
				}

				slog.Debug(fmt.Sprintf("sending pcm data, text: [%s]", msg.text), logTag)
			}

			if pcmFrameRead > 0 {
				pcm.send(rteEnv, buf)
				sentFrames++
				slog.Info(fmt.Sprintf("sending pcm remain data, text: [%s], pcmFrameRead: %d", msg.text, pcmFrameRead), logTag)
			}

			r.Close()
			slog.Info(fmt.Sprintf("send pcm data finished, text: [%s], receivedTs: %d, readBytes: %d, sentFrames: %d, firstFrameLatency: %dms, finishLatency: %dms",
				msg.text, msg.receivedTs, readBytes, sentFrames, firstFrameLatency, time.Since(startTime).Milliseconds()), logTag)
		}
	}()

	rteEnv.OnStartDone()
}

// OnCmd receives cmd from ten graph.
// current supported cmd:
//   - name: flush
//     example:
//     {"name": "flush"}
func (e *fishAudioTTSExtension) OnCmd(
	rteEnv rte.RteEnv,
	cmd rte.Cmd,
) {
	cmdName, err := cmd.GetName()
	if err != nil {
		slog.Error(fmt.Sprintf("OnCmd get name failed, err: %v", err), logTag)
		cmdResult, _ := rte.NewCmdResult(rte.StatusCodeError)
		rteEnv.ReturnResult(cmdResult, cmd)
		return
	}

	slog.Info(fmt.Sprintf("OnCmd %s", cmdInFlush), logTag)

	switch cmdName {
	case cmdInFlush:
		outdateTs.Store(time.Now().UnixMicro())

		// send out
		outCmd, err := rte.NewCmd(cmdOutFlush)
		if err != nil {
			slog.Error(fmt.Sprintf("new cmd %s failed, err: %v", cmdOutFlush, err), logTag)
			cmdResult, _ := rte.NewCmdResult(rte.StatusCodeError)
			rteEnv.ReturnResult(cmdResult, cmd)
			return
		}

		if err := rteEnv.SendCmd(outCmd, nil); err != nil {
			slog.Error(fmt.Sprintf("send cmd %s failed, err: %v", cmdOutFlush, err), logTag)
			cmdResult, _ := rte.NewCmdResult(rte.StatusCodeError)
			rteEnv.ReturnResult(cmdResult, cmd)
			return
		} else {
			slog.Info(fmt.Sprintf("cmd %s sent", cmdOutFlush), logTag)
		}
	}

	cmdResult, _ := rte.NewCmdResult(rte.StatusCodeOk)
	rteEnv.ReturnResult(cmdResult, cmd)
}

// OnData receives data from ten graph.
// current supported data:
//   - name: text_data
//     example:
//     {name: text_data, properties: {text: "hello"}
func (e *fishAudioTTSExtension) OnData(
	rteEnv rte.RteEnv,
	data rte.Data,
) {
	text, err := data.GetPropertyString(dataInTextDataPropertyText)
	if err != nil {
		slog.Warn(fmt.Sprintf("OnData GetProperty %s failed, err: %v", dataInTextDataPropertyText, err), logTag)
		return
	}

	if len(text) == 0 {
		slog.Debug("OnData text is empty, ignored", logTag)
		return
	}

	slog.Info(fmt.Sprintf("OnData input text: [%s]", text), logTag)

	go func() {
		textChan <- &message{text: text, receivedTs: time.Now().UnixMicro()}
	}()
}

func init() {
	// Register addon
	rte.RegisterAddonAsExtension(
		"fish_audio_tts",
		rte.NewDefaultExtensionAddon(newFishAudioTTSExtension),
	)
}

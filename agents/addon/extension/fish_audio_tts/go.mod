module fish_audio_tts

go 1.21

replace agora.io/rte => ../../../interface

require (
	agora.io/rte v0.0.0-00010101000000-000000000000
	github.com/vmihailenco/msgpack/v5 v5.4.1
)

require github.com/vmihailenco/tagparser/v2 v2.0.0 // indirect

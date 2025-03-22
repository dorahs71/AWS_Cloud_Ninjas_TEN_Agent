import { IOptions, ColorItem } from "@/types"

export const REQUEST_URL = process.env.NEXT_PUBLIC_REQUEST_URL ?? ""
export const GITHUB_URL = "https://github.com/Chen188/TEN-Agent"
export const OPTIONS_KEY = "__options__"
export const DEFAULT_OPTIONS: IOptions = {
  channel: "",
  userName: "",
  userId: 0
}
export const DESCRIPTION = "This is an AI voice assistant powered by TEN framework, Agora, Amazon Bedrock, Amazon Transcribe and Amazon SageMaker."
export const MODE_OPTIONS = [
  {
    label: "Chat",
    value: "chat"
  },
  {
    label: "Translate",
    value: "translate"
  }
]
export const GRAPH_NAME_OPTIONS = [
  {
    label: "Dify Knowledge Base",
    value: "va.transcribe-dify.polly",
    desc: "[Chat Mode] Transcribe ASR -> Dify KB -> Polly TTS. Don't allow interrupt before completing prior request."
  },
  {
    label: "transcribe-bedrock-polly-denoising",
    value: "va.transcribe-bedrock.polly.denoising",
    desc: "[Chat Mode] Denoised Transcribe ASR -> Bedrock LLM -> Polly TTS"
  },
  {
    label: "transcribe-bedrock-polly",
    value: "va.transcribe-bedrock.polly",
    desc: "[Chat Mode] Transcribe ASR -> Bedrock LLM -> Polly TTS"
  },
  {
    label: "translate-transcribe-bedrock-polly",
    value: "translate.transcribe-bedrock.polly",
    desc: "[Translation Mode] Transcribe ASR -> Bedrock LLM -> Polly TTS"
  },
  {
    label: "translate-transcribe-bedrock-sagemaker",
    value: "translate.transcribe-bedrock.sagemaker-tts",
    desc: "[Translation Mode] Transcribe ASR -> Bedrock LLM -> SageMaker TTS(You should deploy TTS model first)"
  },
  {
    label: "transcribe-bedrock-sagemaker",
    value: "va.transcribe-bedrock.sagemaker-tts",
    desc: "[Chat Mode] Transcribe ASR -> Bedrock LLM -> SageMaker TTS(deploy TTS model first)"
  },
  {
    label: "transcribe-bedrock-fishaudio",
    value: "va.transcribe-bedrock.fish",
    desc: "[Chat Mode] Transcribe ASR -> Bedrock LLM -> Fish Audio TTS"
  },
  {
    label: "transcribe-sagemaker_llm-polly",
    value: "va.transcribe-sm_llm.polly",
    desc: "[Chat Mode] Transcribe ASR -> SageMaker LLM(deploy LLM first) -> Polly TTS"
  },
  {
    label: "transcribe-sagemaker_llm-sagemaker_tts",
    value: "va.transcribe-sm_llm.sm_tts",
    desc: "[Chat Mode] Transcribe ASR -> SageMaker LLM(deploy LLM first) -> SageMaker TTS(deploy TTS model first)"
  }
]
export const LANG_OPTIONS = [
  {
    label: "English",
    value: "en-US"
  },
  {
    label: "Chinese Simplified",
    value: "zh-CN"
  },
  {
    label: "Chinese Traditional",
    value: "zh-TW"
  },
  {
    label: "Japanese",
    value: "ja-JP"
  },
  {
    label: "French",
    value: "fr-FR"
  },
  {
    label: "Hindi",
    value: "hi-IN"
  }
]
export const VOICE_OPTIONS = [
  {
    label: "Male",
    value: "male"
  },
  {
    label: "Female",
    value: "female"
  }
]
export const COLOR_LIST: ColorItem[] = [{
  active: "#0888FF",
  default: "#112941"
}, {
  active: "#563FD8",
  default: "#221C40"
},
{
  active: "#18A957",
  default: "#112A1E"
}, {
  active: "#FFAB08",
  default: "#392B13"
}, {
  active: "#FD5C63",
  default: "#3C2023"
}, {
  active: "#E225B2",
  default: "#371530"
}]


import { IOptions, ColorItem } from "@/types"

export const REQUEST_URL = process.env.NEXT_PUBLIC_REQUEST_URL ?? ""
export const GITHUB_URL = "https://github.com/rte-design/ASTRA.ai"
export const OPTIONS_KEY = "__options__"
export const DEFAULT_OPTIONS: IOptions = {
  channel: "",
  userName: "",
  userId: 0
}
export const DESCRIPTION = "This is an AI voice assistant powered by ASTRA.ai framework, Agora, Amazon Bedrock, Amazon Transcribe and Amazon SageMaker."
export const MODE_OPTIONS = [
  {
    label: "Translate",
    value: "translate"
  },
  {
    label: "Chat",
    value: "chat"
  }
]
export const GRAPH_NAME_OPTIONS = [
  {
    label: "translate-transcribe-bedrock-polly",
    value: "translate.transcribe-bedrock.polly"
  },
  {
    label: "translate-transcribe-bedrock-sagemaker",
    value: "translate.transcribe-bedrock.sagemaker-tts"
  },
  {
    label: "transcribe-bedrock-sagemaker",
    value: "va.transcribe-bedrock.sagemaker-tts"
  },
  {
    label: "transcribe-bedrock-fishaudio",
    value: "va.transcribe-bedrock.fish"
  },
  {
    label: "transcribe-bedrock-polly",
    value: "va.transcribe-bedrock.polly"
  },
  {
    label: "transcribe-sagemaker_llm-polly",
    value: "va.transcribe-sm_llm.polly"
  },
  {
    label: "transcribe-sagemaker_llm-sagemaker_tts",
    value: "va.transcribe-sm_llm.sm_tts"
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


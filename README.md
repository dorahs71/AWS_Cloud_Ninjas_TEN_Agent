# [Cloud_Ninjas 石虎語音機器人](https://d340gc1xzxnox1.cloudfront.net/)

命題企業 : 長春集團
Cloud_Ninjas 石虎語音機器人是一款基於 TEN Framework 開發的多語音機器人，能夠與使用者進行自然的語音對話。

## 目錄

- [目錄](#目錄)
- [即時演示](#即時演示)
- [主要功能](#主要功能)
- [核心技術](#核心技術)
- [系統架構](#系統架構)
- [後端技術](#後端技術)
- [前端技術](#前端技術)
- [擴展配置](#擴展配置)

## 即時演示

[Demo Video](https://drive.google.com/file/d/1UsNMP1LSYU7lUyZ7ifsKrmsX_AoDUstt/view)
![Cloud_Ninjas 石虎語音機器人](https://github.com/user-attachments/assets/8d924b8f-2586-4c98-84c7-716f0024f547)


## 主要功能

- **實時語音對話**：透過 Amazon Transcribe 轉錄用戶語音輸入，並使用 Amazon Bedrock Nova Pro 模型生成回應
- **函數調用能力**：支援數學計算等工具型功能，透過 Nova Pro 的 function calling 實現
- **即時中斷**：用戶可以在機器人回應過程中隨時打斷並開始新的對話
- **自然流暢響應**：使用 Amazon Polly 合成自然的語音輸出，支援多種引擎（標準、神經網絡、長篇和生成式）
- **多語言支持**：支援多種語言的語音識別和合成
- **可擴展架構**：基於 TEN Framework 的插件系統，可以輕鬆添加新的功能組件

## 核心技術

#### 語音識別 (STT)
[Amazon Transcribe](https://aws.amazon.com/tw/pm/transcribe/?trk=4a32c3d2-f78f-4d92-ad96-aec3dffab4d4&sc_channel=ps&ef_id=Cj0KCQjwiLLABhCEARIsAJYS6umgVa1eaYpcvXH4oYAI25XV9P4pcYLNMT_vw0MmHKTXs52Zt-vXsdcaAmkiEALw_wcB:G:s&s_kwcid=AL!4422!3!652835877972!e!!g!!amazon%20transcribe!19910625970!151321783327&gbraid=0AAAAADjHtp-Mw8Qry3JFf3oO2OnmtgZmV&gclid=Cj0KCQjwiLLABhCEARIsAJYS6umgVa1eaYpcvXH4oYAI25XV9P4pcYLNMT_vw0MmHKTXs52Zt-vXsdcaAmkiEALw_wcB)

#### 大型語言模型
[Amazon Bedrock](https://aws.amazon.com/tw/bedrock/?trk=c0acda64-df2a-4080-9d0d-938d8963b57d&sc_channel=ps&ef_id=Cj0KCQjwiLLABhCEARIsAJYS6uneGsr3ByO6cZQWZYT5AuddrlLwVoYEzb4pnzGdgBQD_BGR6XKqSB0aAgTjEALw_wcB:G:s&s_kwcid=AL!4422!3!692062175189!e!!g!!amazon%20bedrock!21054971942!158684192785&gbraid=0AAAAADjHtp9WAgvzcS5eZS-FHVGXt86mj&gclid=Cj0KCQjwiLLABhCEARIsAJYS6uneGsr3ByO6cZQWZYT5AuddrlLwVoYEzb4pnzGdgBQD_BGR6XKqSB0aAgTjEALw_wcB)

#### 語音合成 (TTS)
[Amazon Polly](https://aws.amazon.com/tw/polly/)

#### 實時通信
[Agora RTC](https://www.agora.io/en/)

### 數據流架構
```
+----------------+    +------------------+    +----------------+
|                |    |                  |    |                |
|   Agora RTC    +---->  Transcribe ASR  +---->  Bedrock LLM   |
|                |    |                  |    |                |
+-------+--------+    +------------------+    +--------+-------+
        ^                                              |
        |                                              |
        |                                              v
        |                                     +----------------+
        |                                     |                |
        +-------------------------------------+   Polly TTS    |
                                              |                |
                                              +----------------+
```

## 後端技術

### 框架

- TEN Framework (Rust)
- Python Extensions

### 雲服務

- AWS Bedrock
- AWS Transcribe
- AWS Polly
- AWS CloudFront
- Agora RTC

### 部署

- Docker
- Docker Compose

### 版本控制

- Git / GitHub

## 前端技術

- HTML / CSS / JavaScript
- WebRTC
- WebSocket
- Next.js

## 擴展配置

Cloud_Ninjas_Agent 使用 JSON 配置文件定義擴展和數據流。以下是主要的擴展配置：

### Amazon Bedrock LLM 擴展

```json
{
  "type": "extension",
  "extension_group": "bedrock",
  "addon": "bedrock_llm_python",
  "name": "bedrock_llm",
  "property": {
    "region": "us-west-2",
    "access_key": "XXXXXXXXXXXXX",
    "secret_key": "XXXXXXXXXXXXX",
    "model": "us.amazon.nova-pro-v1:0",
    "max_tokens": 512,
    "prompt": "",
    "greeting": "長春集團石虎機器人已上線，我可以幫助你什麼",
    "max_memory_length": 10,
    "enable_function_calling": true
  }
}
```

### Amazon Transcribe 擴展

```json
{
  "type": "extension",
  "extension_group": "asr",
  "addon": "transcribe_asr",
  "name": "transcribe_asr",
  "property": {
    "region": "us-west-2",
    "access_key": "XXXXXXXXXXXXX",
    "secret_key": "XXXXXXXXXXXXX",
    "sample_rate": "16000",
    "lang_code": "zh-TW"
  }
}
```

### Amazon Polly 擴展

```json
{
  "type": "extension",
  "extension_group": "tts",
  "addon": "polly_tts",
  "name": "polly_tts",
  "property": {
    "region": "us-west-2",
    "access_key": "XXXXXXXXXXXXX",
    "secret_key": "XXXXXXXXXXXXX",
    "engine": "neural",
    "voice": "Zhiyu",
    "sample_rate": "16000",
    "lang_code": "cmn-CN"
  }
}
```

### 功能擴展

系統支援使用 function calling 擴展功能，例如計算器：

```json
"calculator": {
  "description": "計算加減乘除的工具，可以處理基本數學運算",
  "inputSchema": {
    "operation": "運算類型，支持: add, subtract, multiply, divide",
    "numbers": "要計算的數字列表"
  }
}
```

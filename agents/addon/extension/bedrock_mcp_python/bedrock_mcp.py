from openai import OpenAI
import random
from typing import Dict, List, Optional


class BedrockMcpConfig:
    def __init__(self,
                 api_key: str,
                 base_url: str,
                 max_tokens: int,
                 model: str,
                 prompt: str,
                 temperature: float,
                 top_p: float,
                 top_k: float,
                 mcp_server_ids: str):
        self.api_key = api_key
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.model = model
        self.prompt = prompt
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.mcp_server_ids = mcp_server_ids

    @classmethod
    def default_config(cls):
        return cls(
            api_key="",
            base_url="",
            max_tokens=4000,
            model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            prompt="You are a voice assistant who talks in a conversational way and can chat with me like my friends. I will speak to you in English or Chinese, and you will answer in the corrected and improved version of my text with the language I use. Don’t talk like a robot, instead I would like you to talk like a real human with emotions. I will use your answer for text-to-speech, so don’t return me any meaningless characters. I want you to be helpful, when I’m asking you for advice, give me precise, practical and useful advice instead of being vague. When giving me a list of options, express the options in a narrative way instead of bullet points.",
            temperature=0.5,
            top_p=0.9,
            top_k=200,
            mcp_server_ids=""
        )

    def validate(self):
        assert len(self.base_url) > 0, "MCP BASE URL is required"

        if self.mcp_server_ids:
            self.mcp_server_ids = self.mcp_server_ids.split(',')
        else:
            self.mcp_server_ids = []

class BedrockMcp:
    def __init__(self, config: BedrockMcpConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

    def get_chat_completions_stream(self, messages: List[Dict[str, str]]):
        kwargs = {
            "max_tokens": self.config.max_tokens,
            "messages": [
                {
                    "role": "system",
                    "content": self.config.prompt,
                },
                *messages,
            ],
            "model": self.config.model,
            "stream": True,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
        }
        
        if self.config.mcp_server_ids:
            kwargs["extra_body"] = {
                "mcp_server_ids": self.config.mcp_server_ids,
                "top_k": self.config.top_k,
            }

        response = self.client.chat.completions.create(**kwargs)
        return response
from dataclasses import dataclass
import requests
import json
from .log import logger
# from log import logger

@dataclass
class DifyLLMConfig:
    base_url: str = "https://api.dify.ai/v1"
    api_key: str = ""
    user_id: str = "TenAgent"
    greeting: str = "How can I help you today?"
    failure_info: str = "Sorry, I am unable to process your request at the moment."
    max_history: int = 32  # not used here, will use dify conversation_id for multi-round chat.

    @staticmethod
    def default_config():
        return DifyLLMConfig()

    def validate(self):
        if not self.api_key:
            raise ValueError("API key is required")
        if not self.base_url:
            raise ValueError("Base URL is required")

class DifyLLM:
    def __init__(self, config: DifyLLMConfig):
        self.config = config
        self.conversation_id = None

    def get_chat_stream(self, messages):
        """
        Get a streaming response from Dify API
        
        Args:
            messages: List of message objects with role and content
            
        Returns:
            A requests.Response object with streaming content
        """
        try:
            # Extract the latest user message
            latest_message = messages[-1]["content"] if messages else ""
            if isinstance(latest_message, list) and len(latest_message) > 0:
                if isinstance(latest_message[0], dict) and "text" in latest_message[0]:
                    latest_message = latest_message[0]["text"]
            
            payload = {
                "inputs": {},
                "query": latest_message,
                "response_mode": "streaming",
                "user": self.config.user_id,
                "auto_generate_name": False
            }

            if self.conversation_id:
                payload["conversation_id"] = self.conversation_id

            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            }

            url = f"{self.config.base_url}/chat-messages"
            
            # Use requests with stream=True to get a streaming response
            response = requests.post(url, json=payload, headers=headers, stream=True)
            
            if response.status_code != 200:
                logger.error(f"Received error response: {response.json()}")
                return None

            return response

        except Exception as e:
            logger.error(f"Error in chat stream: {str(e)}")
            return None
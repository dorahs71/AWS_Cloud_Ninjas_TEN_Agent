import boto3
from .log import logger
from .bedrock_llm_config import BedrockLLMConfig

class BedrockLLM:
    client = None
    def __init__(self, config: BedrockLLMConfig):
        self.config = config

        if config.access_key and config.secret_key:
            logger.info(f"BedrockLLM initialized with access key: {config.access_key}")

            self.client = boto3.client(service_name='bedrock-runtime', 
                                    region_name=config.region,
                                    aws_access_key_id=config.access_key,
                                    aws_secret_access_key=config.secret_key)
        else:
            logger.info(f"BedrockLLM initialized without access key, using default credentials provider chain.")
            self.client = boto3.client(service_name='bedrock-runtime', region_name=config.region)

    def get_converse_resp(self, messages, stream=True, **override_params):
        bedrock_req_params = {
            "modelId": self.config.model,
            "messages": messages,
            "inferenceConfig": {
                "temperature": self.config.temperature,
                "maxTokens": self.config.max_tokens,
                "topP": self.config.top_p,
                "stopSequences": ["</translation>"],
            },
            # "additionalModelRequestFields": additional_model_fields,
        }

        if self.config.prompt:
            bedrock_req_params['system'] = [
                {'text': self.config.prompt}
            ]

        bedrock_req_params.update(override_params)

        try:
            if stream:
                response = self.client.converse_stream(**bedrock_req_params)
            else:
                response = self.client.converse(**bedrock_req_params)
            return response
        except Exception as e:
            logger.exception(f"get_converse_resp failed, err: {e}")
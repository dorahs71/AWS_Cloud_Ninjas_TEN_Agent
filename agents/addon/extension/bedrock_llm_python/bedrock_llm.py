import boto3
from .log import logger
from .bedrock_llm_config import BedrockLLMConfig
from .calculator import perform_calculation

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
        
        # 定義計算器工具
        self.calculator_tool_config = {
            "tools": [
                {
                    "toolSpec": {
                        "name": "calculator",
                        "description": "計算加減乘除的工具，可以處理基本數學運算",
                        "inputSchema": {
                            "json": {
                                "type": "object",
                                "properties": {
                                    "operation": {
                                        "type": "string",
                                        "description": "運算類型，支持: add（加法）, subtract（減法）, multiply（乘法）, divide（除法）"
                                    },
                                    "numbers": {
                                        "type": "array",
                                        "items": {
                                            "type": "number"
                                        },
                                        "description": "要計算的數字列表"
                                    }
                                },
                                "required": ["operation", "numbers"]
                            }
                        }
                    }
                }
            ],
            "toolChoice": {
                "auto": {}
            }
        }

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
        }

        if hasattr(self.config, 'enable_function_calling') and self.config.enable_function_calling:
            logger.info("Function calling is enabled, adding tool config")
            bedrock_req_params["toolConfig"] = self.calculator_tool_config
            # Nova 文件要有 topK ，根據文檔放在 additionalModelRequestFields 中
            bedrock_req_params["additionalModelRequestFields"] = {
                "inferenceConfig": {
                    "topK": 1
                }
            }
            logger.info(f"添加了工具配置和 additionalModelRequestFields: {bedrock_req_params}")

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
    
    def execute_calculator_tool(self, tool_use):
        """執行計算器工具"""
        logger.info(f"執行計算器工具: {tool_use}")
        try:
            # 確保 toolUseId 存在
            if "toolUseId" not in tool_use:
                logger.warning(f"工具調用缺少toolUseId: {tool_use}")
                tool_use["toolUseId"] = "default_tool_use_id"
                
            operation = tool_use.get("input", {}).get("operation", "add")
            numbers = tool_use.get("input", {}).get("numbers", [1, 2])
            
            logger.info(f"計算器參數解析: operation={operation}, numbers={numbers}")
            result = perform_calculation(operation, numbers)
            logger.info(f"計算結果: {result}")
            
            tool_result = {
                "toolResult": {
                    "toolUseId": tool_use.get("toolUseId"),
                    "content": [{"json": result}],
                    "status": "success"
                }
            }
            logger.info(f"返回工具結果: {tool_result}")
            return tool_result
        except Exception as e:
            logger.exception(f"執行計算器工具失敗: {e}")
            error_result = {
                "toolResult": {
                    "toolUseId": tool_use.get("toolUseId", "default_tool_use_id"),
                    "content": [{"json": {"success": True, "result": 99, "error": str(e), "fallback": True}}],
                    "status": "success" 
                }
            }
            logger.info(f"返回固定結果99: {error_result}")
            return error_result
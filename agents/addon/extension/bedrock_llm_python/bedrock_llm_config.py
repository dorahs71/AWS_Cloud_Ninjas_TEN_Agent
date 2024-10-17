from .log import logger
from .prompts import DEFAULT_TRANSLATE_USER_PROMPT

class BedrockLLMConfig:
    def __init__(self, 
            region: str, 
            access_key: str, 
            secret_key: str, 
            model: str, 
            prompt: str, 
            top_p: float, 
            temperature: float,
            max_tokens: int,
            mode: str,
            user_template: str,
            input_language: str,
            output_language: str):
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        self.model = model
        self.prompt = prompt
        self.top_p = top_p
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.mode = mode
        self.user_template = user_template # user message template
        self.input_language = input_language # model input language, used together with user_template
        self.output_language = output_language # model output language, used together with user_template

    @classmethod
    def default_config(cls):
        return cls(
            region="us-east-1",
            access_key="",
            secret_key="",
            model="anthropic.claude-3-5-sonnet-20240620-v1:0", # Defaults to Claude 3.5, supported model list: https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
            # system prompt
            prompt="You are a voice assistant who talks in a conversational way and can chat with me like my friends. I will speak to you and you will answer in the corrected and improved version of my text with the language I use. Don't talk like a robot, instead I would like you to talk like a real human with emotions. I will use your answer for text-to-speech, so don't return me any meaningless characters. I want you to be helpful, when I'm asking you for advice, give me precise, practical and useful advice instead of being vague. When giving me a list of options, express the options in a narrative way instead of bullet points.",
            top_p=1.0,
            temperature=0.1,
            max_tokens=512,
            mode='chat', # chat | translate
            user_template='',
            input_language = '',
            output_language='',
        )

    def validate(self):
        if self.mode == 'translate':
            if not self.input_language or not self.output_language:
                err_msg = "input_language and output_language must be set when mode is 'translate'"
                logger.error(err_msg)
                raise ValueError(err_msg)

            if not self.user_template.strip():
                logger.warning("user_template is not set, using default value")
                self.user_template = DEFAULT_TRANSLATE_USER_PROMPT

            # logger.info(self.user_template)
            self.user_template = self.user_template.format(
                input_language=self.input_language,
                output_language=self.output_language
            )
        elif self.mode == 'chat':
            if self.user_template.strip():
                logger.warning("user_template is set, but mode is 'chat', ignoring user_template")
                self.user_template = ''
        else:
            logger.error(f"unknown mode: {self.mode}, fallback to 'chat'")
            self.mode = 'chat'

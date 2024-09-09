import re
from dataclasses import dataclass
from typing import Union, List, Dict
from rte import Data
from .property import *
from .prompts import *
from .utils import *
from .log import logger
from .property import PUNCUTATIONS

class DataParserBase:
    def __init__(self, user_template: str='') -> None:
        self.user_template = user_template
        self.language = None

    @property
    def language(self) -> str:
        return self._language

    @language.setter
    def language(self, new_lang: str) -> None:
        self._language = new_lang

    @staticmethod
    def get_properties(data: Data, properties: List[str]):
        result = {}
        for property in properties:
            value = None
            try:
                if property not in DATA_IN_TYPES:
                    logger.warning(f"property[{property}] not in DATA_IN_TYPES[{DATA_IN_TYPES}]")

                value = getattr(data, f"get_property_{DATA_IN_TYPES[property]}")(property)
            except Exception as err:
                logger.debug(f"GetProperty {property} failed, err: {err}")

            result[property] = value
        return result

    def format_user_input(self, input_text: str) -> Union[str, None]:
        if not input_text:
            return None

        if self.user_template:
            try:
                return self.user_template.format(input_text=input_text)
            except Exception as err:
                logger.exception(f"Apply user template failed, err: {err}. User template disabled.")
                self.user_template = None

        return input_text


class DataParserChat(DataParserBase):
    def parse(self, data: Data, bedrock_llm) -> Union[str, None]:
        properties = self.get_properties(data, [
            DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL,
            DATA_IN_TEXT_DATA_PROPERTY_TEXT
        ])

        if not properties[DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL]:
            logger.info("ignore non-final input")
            return

        if not properties[DATA_IN_TEXT_DATA_PROPERTY_TEXT]:
            logger.info("ignore empty text")
            return

        return self.format_user_input(input_text=properties[DATA_IN_TEXT_DATA_PROPERTY_TEXT])


class DataParserTranslate(DataParserBase):
    def __init__(self, user_template: str = '', min_length: int = 8, min_new_words: int = 6) -> None:
        super().__init__(user_template)
        self.min_length = min_length # min text length before leveraging llm
        self.min_new_words = min_new_words # if last llm request failed, wait x more words.
        self.reset_status()

    def reset_status(self):
        self.last_failed_llm_length = 0
        self.working = False
        self.translated_text = ""

    def parse(self, data: Data, bedrock_llm) -> Union[str, None]:
        if self.working:
            logger.info("Already processing, skipping this request")
            return None

        try:
            self.working = True
            properties = self.get_properties(
                data,
                [
                    DATA_IN_TEXT_DATA_PROPERTY_LANGUAGE,
                    DATA_IN_TEXT_DATA_PROPERTY_TEXT,
                    DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL,
                    DATA_IN_TEXT_DATA_PROPERTY_TEXT_STABLE,
                    DATA_IN_TEXT_DATA_PROPERTY_TEXT_NON_STABLE
                ]
            )

            if properties[DATA_IN_TEXT_DATA_PROPERTY_LANGUAGE]:
                self.language = properties[DATA_IN_TEXT_DATA_PROPERTY_LANGUAGE]

            if not (properties[DATA_IN_TEXT_DATA_PROPERTY_TEXT_STABLE] or properties[DATA_IN_TEXT_DATA_PROPERTY_TEXT_NON_STABLE]):
                logger.info("Translate without partial stable")
                return self.parse_without_stable(properties)
            else:
                return self.parse_with_stable(properties, bedrock_llm)
        finally:
            self.working = False

    def parse_without_stable(self, properties: Dict) -> Union[str, None]:
        if not properties[DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL]:
            logger.info("Ignore non-final input")
            return None

        if not properties[DATA_IN_TEXT_DATA_PROPERTY_TEXT]:
            logger.info("Ignore empty text")
            return None

        return self.format_user_input(input_text=properties[DATA_IN_TEXT_DATA_PROPERTY_TEXT])

    def parse_with_stable(self, properties: Dict, bedrock_llm) -> Union[str, None]:
        stable_text = properties[DATA_IN_TEXT_DATA_PROPERTY_TEXT_STABLE]

        if not stable_text:
            # logger.info('No stable text found, return')
            return None

        remained_text = stable_text[len(self.translated_text):]
        # logger.info(f"Processing remained_text: {remained_text}")

        if properties[DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL]:
            self.reset_status()
            logger.info(f'Got final text, processing remained text[{remained_text}]')
            return self.format_user_input(input_text=remained_text) if remained_text else None

        content, found_punc = get_content_before_last_punctuation(remained_text)
        # logger.info(f"content: {content}, found_punc: {found_punc}.")

        if found_punc:
            self.translated_text += content
            logger.info('Found puncation in transcribe result, processing without invoking LLM')
            return self.format_user_input(input_text=content)
        
        non_stable_text = properties[DATA_IN_TEXT_DATA_PROPERTY_TEXT_NON_STABLE]
        _, non_stable_found_punc = get_content_before_last_punctuation(non_stable_text)

        if non_stable_found_punc:
            logger.info('Found puncation in non stable result, waiting for its stablization.')
            return

        if not self.should_process_with_llm(remained_text):
            return None

        logger.info(f"Using llm to add punc into: [{remained_text}]")
        return self.process_with_llm(prior_asr_content=self.translated_text, remained_text=remained_text, bedrock_llm=bedrock_llm)

    def should_process_with_llm(self, remained_text: str) -> bool:
        remained_text_len = count_word(self.language, remained_text)
        logger.info(f"lanauge: {self.language}, content: {remained_text}, length: {remained_text_len}")
        return (remained_text_len >= self.min_length and
                remained_text_len - self.last_failed_llm_length > self.min_new_words)

    def process_with_llm(self, prior_asr_content: str, remained_text: str, bedrock_llm) -> Union[str, None]:
        try:
            resp = self.get_llm_response(prior_asr_content, remained_text, bedrock_llm)
            output_text = self.extract_output_text(resp, remove_tail_punc=True)

            logger.info(f"Punc LLM response [{output_text}]")

            consumed_text, text_with_punc = self.consume_llm_output(remained_text, output_text, False)
            if not consumed_text:
                self.last_failed_llm_length = count_word(self.language, remained_text)
                return None

            self.last_failed_llm_length = 0
            self.translated_text += consumed_text
            return self.format_user_input(input_text=text_with_punc)
        except Exception as e:
            logger.error(f"Error processing with LLM: {e}")
            return None

    def get_llm_response(self, prior_asr_content: str, remained_text: str, bedrock_llm):
        return bedrock_llm.get_converse_resp(
            messages=[
                {'role': 'user', 'content': [{"text": DEFAULT_PUNCATION_PROMPT.format(content=remained_text, prior_asr_content=prior_asr_content)}]}
            ],
            stream=False,
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            inferenceConfig={
                "temperature": 0,
                "maxTokens": 100,
            },
        )

    def extract_output_text(self, resp: Dict, remove_tail_punc: bool) -> str:
        output_message = resp.get('output', {}).get('message', {})
        if not output_message:
            raise ValueError(f"Invalid LLM response: {resp}")

        content = output_message.get('content', [{}])[0].get('text', '')

        if remove_tailing_punctuations:
            content = remove_tailing_punctuations(content)

        return content

    def consume_llm_output(self, original_text: str, llm_output: str, strict_mode=False):
        if len(original_text) >= len(llm_output):
            return '', ''

        if strict_mode:
            """严格匹配模型返回结果（去除标点）"""
            original_without_punc = re.sub(rf"[{''.join(PUNCUTATIONS + [' '])}]", '', original_text)
            new_without_punc = re.sub(rf"[{''.join(PUNCUTATIONS + [' '])}]", '', llm_output)

            if original_without_punc != new_without_punc:
                logger.warning(f"Failed to add punctuation: text with new punctuation is [{new_without_punc}], it doesn't match original text:[{original_without_punc}]. Dropping it.")
                self.last_failed_llm_length = count_word(self.language, original_text)
                return '', ''

            return original_text, llm_output
        else:
            idx = 0
            punc_idx = -1
            consumed_cnt = 0

            for llm_idx, char in enumerate(llm_output):
                if idx < len(original_text):
                    if char == original_text[idx]:
                        idx += 1
                        consumed_cnt = idx
                        punc_idx = llm_idx
                    elif char in PUNCUTATIONS:
                        punc_idx = llm_idx
                    else:
                        break
                else:
                    if char in PUNCUTATIONS:
                        punc_idx = llm_idx
                    else:
                        break

            return original_text[:consumed_cnt], llm_output[:punc_idx + 1]
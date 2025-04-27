PROPERTY_REGION = "region"  # Optional
PROPERTY_ACCESS_KEY = "access_key"  # Optional
PROPERTY_SECRET_KEY = "secret_key"  # Optional
PROPERTY_MODEL = "model"  # Optional
PROPERTY_PROMPT = "prompt"  # Optional
PROPERTY_TEMPERATURE = "temperature"  # Optional
PROPERTY_TOP_P = "top_p"  # Optional
PROPERTY_MAX_TOKENS = "max_tokens"  # Optional
PROPERTY_GREETING = "greeting"  # Optional
PROPERTY_MAX_MEMORY_LENGTH = "max_memory_length"  # Optional
PROPERTY_MODE = "mode"  # Optional
PROPERTY_INPUT_LANGUAGE = "input_language"  # Optional
PROPERTY_OUTPUT_LANGUAGE = "output_language"  # Optional
PROPERTY_USER_TEMPLATE = "user_template"  # Optional
PROPERTY_ENABLE_FUNCTION_CALLING = "enable_function_calling"  # Optional

CMD_IN_FLUSH = "flush"
CMD_OUT_FLUSH = "flush"

DATA_IN_TEXT_DATA_PROPERTY_LANGUAGE = 'language'
DATA_IN_TEXT_DATA_PROPERTY_TEXT = "text"
DATA_IN_TEXT_DATA_PROPERTY_TEXT_STABLE = "text_stable"
DATA_IN_TEXT_DATA_PROPERTY_TEXT_NON_STABLE = "text_non_stable"
DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL = "is_final"
DATA_OUT_TEXT_DATA_PROPERTY_TEXT = "text"
DATA_OUT_TEXT_DATA_PROPERTY_TEXT_END_OF_SEGMENT = "end_of_segment"

DATA_IN_TYPES = {
    DATA_IN_TEXT_DATA_PROPERTY_LANGUAGE: "string",
    DATA_IN_TEXT_DATA_PROPERTY_TEXT: "string",
    DATA_IN_TEXT_DATA_PROPERTY_TEXT_STABLE: "string",
    DATA_IN_TEXT_DATA_PROPERTY_TEXT_NON_STABLE: "string",
    DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL: "bool",
}

PUNCUTATIONS = set(",，.。?？!！")
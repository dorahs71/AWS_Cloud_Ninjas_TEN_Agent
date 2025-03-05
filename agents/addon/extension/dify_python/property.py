EXTENSION_NAME='dify_python'

# Properties
PROPERTY_BASE_URL = "base_url"  # Required
PROPERTY_API_KEY = "api_key"  # Required
PROPERTY_USER_ID = "user_id"  # Optional
PROPERTY_GREETING = "greeting"  # Optional
PROPERTY_FAILURE_INFO = "failure_info"  # Optional
PROPERTY_MAX_HISTORY = "max_history"  # Optional

# Commands
CMD_IN_FLUSH = "flush"
CMD_OUT_FLUSH = "flush"

# Data properties
DATA_IN_TEXT_DATA_PROPERTY_TEXT = "text"
DATA_IN_TEXT_DATA_PROPERTY_IS_FINAL = "is_final"
DATA_OUT_TEXT_DATA_PROPERTY_TEXT = "text"
DATA_OUT_TEXT_DATA_PROPERTY_END_OF_SEGMENT = "end_of_segment"

# Punctuation for sentence parsing
PUNCUTATIONS = set(",，.。?？!！")
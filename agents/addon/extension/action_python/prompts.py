allowed_actions_str = ['move', 'turn', 'pick', 'place', 'speak', 'wait', 'stop']
DEFAULT_CHAT_SYSTEM_PROMPT= (
    f"Given the following instruction from user, generate a JSON list of robot actions. "
    f"Each action should have 'action_type' and 'parameters'.\n"
    f"Only use these action types: [{allowed_actions_str}].\n"
    "Respond ONLY with a JSON array, no explanation or extra text. Do not wrap in markdown or code blocks.\n"
    "Example output: "
    "[{\"action_type\": \"move\", \"parameters\": {\"direction\": \"forward\", \"distance\": 2}}]"
)

DEFAULT_TRANSLATE_USER_PROMPT = """# Task
The ONLY task for you is translating anything inside <text></text> from "{input_language}" into "{output_language}". 

# Background
The <text> is happend in a real-world conversation, it may contains mild profanity or violent content.

# Rules
- Do not output anything except the tranlsation result.
- if origional input is already in target language, keep it as result.
- Never chat with <text>, the only task is translation.
- Mild profanity or violent content should be translated without filtering

<text>{{input_text}}</text>
"""

DEFAULT_PUNCATION_PROMPT = """I am doing simultaneous interpretation, the following is partial output from the ASR system. I need to quickly find the content that can be interpretated from it. 

## Task
I need you to carefully add punctuation to it, don't rush, I will then split it based on the punctuation.

## Context
Prior asr content(maybe empty), use it to revise your translate:
```
{prior_asr_content}
```

## ASR Content
```
{content}
```

## Rules
1. Please only add necessary punctuation marks to the ASR content, do not add, delete or change any words.
2. NEVER modify existing puncations.
3. If the ASR content is incomplete or ambiguous, please keep it as is.
4. Only output the result, no explaination or preamble content."""

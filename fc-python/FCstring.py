import re
import os
import json
import time
from openai import OpenAI
import sys
import requests
from config import OPENAI_API_KEY, BASE_URL, MODEL_NAME

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=BASE_URL
)
print("client started")

def count_words(text: str) -> int:
    """Count the number of words in a text."""
    return len(text.split())

def find_substring(text: str, substring: str) -> dict:
    """Find all occurrences of a substring in a text."""
    positions = [m.start() for m in re.finditer(re.escape(substring), text)]
    return {
        "count": len(positions),
        "positions": positions
    }

def extract_emails(text: str) -> list:
    """Extract all email addresses from a text."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

def word_frequency(text: str) -> dict:
    """Calculate word frequency in a text."""
    words = text.lower().split()
    frequency = {}
    for word in words:
        word = re.sub(r'[^\w\s]', '', word)
        if word:
            frequency[word] = frequency.get(word, 0) + 1
    return frequency

def text_statistics(text: str) -> dict:
    """Calculate various text statistics."""
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
        "avg_sentence_length": len(words) / len(sentences) if sentences else 0
    }

def format_text(text: str, max_length: int = 80) -> str:
    """Format text to fit within a maximum line length."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)

tools = [{
    "type": "function",
    "function": {
        "name": "count_words",
        "description": "Count the number of words in a text",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to count words in"
                }
            },
            "required": ["text"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "find_substring",
        "description": "Find all occurrences of a substring in a text",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to search in"
                },
                "substring": {
                    "type": "string",
                    "description": "The substring to find"
                }
            },
            "required": ["text", "substring"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "extract_emails",
        "description": "Extract all email addresses from a text",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to extract emails from"
                }
            },
            "required": ["text"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "word_frequency",
        "description": "Calculate word frequency in a text",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze"
                }
            },
            "required": ["text"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "text_statistics",
        "description": "Calculate various text statistics",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to analyze"
                }
            },
            "required": ["text"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "format_text",
        "description": "Format text to fit within a maximum line length",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to format"
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum line length (default: 80)"
                }
            },
            "required": ["text"],
            "additionalProperties": False
        }
    }
}]

def function_call_playground(prompt: str):
    messages = [
        {"role": "system", "content": prompt}
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.01,
        stream=False,
        top_p=0.95,
        tools=tools
    )

    func1_name = response.choices[0].message.tool_calls[0].function.name
    func1_args = response.choices[0].message.tool_calls[0].function.arguments
    func1_out = eval(f'{func1_name}(**{func1_args})')

    messages.append(response.choices[0].message)
    messages.append({
        'role': 'tool',
        'content': f'{func1_out}',
        'tool_call_id': response.choices[0].message.tool_calls[0].id
    })

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.01,
        stream=False,
        top_p=0.95,
        tools=tools
    )

    return response.choices[0].message.content

# Test prompts
prompts = [
    "Count the words in this text: Hello world, this is a test message.",
    "Find all occurrences of 'the' in this text: The quick brown fox jumps over the lazy dog.",
    "Extract email addresses from this text: Contact us at test@example.com or support@company.com",
    "Calculate word frequency in this text: The cat and the dog and the cat and the mouse",
    "Get text statistics for this text: This is a test. It has multiple sentences! How many words?",
    "Format this text to 40 characters per line: This is a long text that needs to be formatted to fit within a specific line length while maintaining readability."
]

if __name__ == "__main__":
    for prompt in prompts:
        start_time = time.time()
        print(f"\nPrompt: {prompt}")
        print(f"Response: {function_call_playground(prompt)}")
        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.2f} seconds") 
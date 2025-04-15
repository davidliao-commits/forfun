import re
import os
import json
import time
from openai import OpenAI
import sys
import requests
from typing import Any, Dict, List, Union
from datetime import datetime
from config import OPENAI_API_KEY, BASE_URL, MODEL_NAME
client = OpenAI(
     base_url=BASE_URL,
     api_key=OPENAI_API_KEY
)
print("client started")

def validate_email(email: str) -> Dict[str, Any]:
    """Validate an email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email))
    return {
        "is_valid": is_valid,
        "message": "Valid email address" if is_valid else "Invalid email address format"
    }

def validate_phone(phone: str) -> Dict[str, Any]:
    """Validate a phone number format."""
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', phone)
    is_valid = len(digits) >= 10 and len(digits) <= 15
    return {
        "is_valid": is_valid,
        "message": "Valid phone number" if is_valid else "Invalid phone number format",
        "normalized": digits if is_valid else None
    }

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength."""
    checks = {
        "length": len(password) >= 8,
        "uppercase": bool(re.search(r'[A-Z]', password)),
        "lowercase": bool(re.search(r'[a-z]', password)),
        "digit": bool(re.search(r'\d', password)),
        "special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    }
    
    is_valid = all(checks.values())
    missing = [k for k, v in checks.items() if not v]
    
    return {
        "is_valid": is_valid,
        "message": "Strong password" if is_valid else f"Password missing: {', '.join(missing)}",
        "checks": checks
    }

def validate_json_schema(data: Dict, schema: Dict) -> Dict[str, Any]:
    """Validate data against a JSON schema."""
    errors = []
    
    def validate_type(value: Any, expected_type: str) -> bool:
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict)
        return False
    
    def check_required(data: Dict, required: List[str]) -> List[str]:
        return [field for field in required if field not in data]
    
    def validate_field(value: Any, field_schema: Dict, field_name: str) -> List[str]:
        field_errors = []
        
        # Check type
        if "type" in field_schema:
            if not validate_type(value, field_schema["type"]):
                field_errors.append(f"{field_name} should be of type {field_schema['type']}")
        
        # Check required
        if field_schema.get("required", False) and value is None:
            field_errors.append(f"{field_name} is required")
        
        # Check minimum/maximum for numbers
        if field_schema["type"] == "number":
            if "minimum" in field_schema and value < field_schema["minimum"]:
                field_errors.append(f"{field_name} must be at least {field_schema['minimum']}")
            if "maximum" in field_schema and value > field_schema["maximum"]:
                field_errors.append(f"{field_name} must be at most {field_schema['maximum']}")
        
        # Check minLength/maxLength for strings
        if field_schema["type"] == "string":
            if "minLength" in field_schema and len(value) < field_schema["minLength"]:
                field_errors.append(f"{field_name} must be at least {field_schema['minLength']} characters")
            if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
                field_errors.append(f"{field_name} must be at most {field_schema['maxLength']} characters")
        
        return field_errors
    
    # Check required fields
    if "required" in schema:
        missing = check_required(data, schema["required"])
        if missing:
            errors.extend([f"Missing required field: {field}" for field in missing])
    
    # Validate each field
    for field_name, field_schema in schema.get("properties", {}).items():
        if field_name in data:
            errors.extend(validate_field(data[field_name], field_schema, field_name))
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "message": "Valid data" if len(errors) == 0 else "Validation failed"
    }

def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> Dict[str, Any]:
    """Validate a date string format."""
    try:
        datetime.strptime(date_str, format)
        return {
            "is_valid": True,
            "message": "Valid date format",
            "parsed_date": date_str
        }
    except ValueError:
        return {
            "is_valid": False,
            "message": f"Invalid date format. Expected format: {format}",
            "parsed_date": None
        }

def validate_ip_address(ip: str) -> Dict[str, Any]:
    """Validate an IP address format."""
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        is_valid = all(0 <= int(part) <= 255 for part in parts)
        return {
            "is_valid": is_valid,
            "version": "IPv4" if is_valid else "Invalid",
            "message": "Valid IPv4 address" if is_valid else "Invalid IPv4 address"
        }
    elif re.match(ipv6_pattern, ip):
        return {
            "is_valid": True,
            "version": "IPv6",
            "message": "Valid IPv6 address"
        }
    else:
        return {
            "is_valid": False,
            "version": "Unknown",
            "message": "Invalid IP address format"
        }

tools = [{
    "type": "function",
    "function": {
        "name": "validate_email",
        "description": "Validate an email address format",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "The email address to validate"
                }
            },
            "required": ["email"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "validate_phone",
        "description": "Validate a phone number format",
        "parameters": {
            "type": "object",
            "properties": {
                "phone": {
                    "type": "string",
                    "description": "The phone number to validate"
                }
            },
            "required": ["phone"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "validate_password",
        "description": "Validate password strength",
        "parameters": {
            "type": "object",
            "properties": {
                "password": {
                    "type": "string",
                    "description": "The password to validate"
                }
            },
            "required": ["password"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "validate_json_schema",
        "description": "Validate data against a JSON schema",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "The data to validate"
                },
                "schema": {
                    "type": "object",
                    "description": "The JSON schema to validate against"
                }
            },
            "required": ["data", "schema"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "validate_date_format",
        "description": "Validate a date string format",
        "parameters": {
            "type": "object",
            "properties": {
                "date_str": {
                    "type": "string",
                    "description": "The date string to validate"
                },
                "format": {
                    "type": "string",
                    "description": "The expected date format (default: %Y-%m-%d)"
                }
            },
            "required": ["date_str"],
            "additionalProperties": False
        }
    }
}, {
    "type": "function",
    "function": {
        "name": "validate_ip_address",
        "description": "Validate an IP address format",
        "parameters": {
            "type": "object",
            "properties": {
                "ip": {
                    "type": "string",
                    "description": "The IP address to validate"
                }
            },
            "required": ["ip"],
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
    "Validate this email address: user@example.com",
    "Validate this phone number: +1-555-123-4567",
    "Validate this password: Password123!",
    "Validate this data against the schema: {'name': 'John', 'age': 30} with schema {'type': 'object', 'properties': {'name': {'type': 'string'}, 'age': {'type': 'number', 'minimum': 0, 'maximum': 120}}, 'required': ['name', 'age']}",
    "Validate this date format: 2023-12-31",
    "Validate this IP address: 192.168.1.1"
]

if __name__ == "__main__":
    for prompt in prompts:
        start_time = time.time()
        print(f"\nPrompt: {prompt}")
        print(f"Response: {function_call_playground(prompt)}")
        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.2f} seconds") 
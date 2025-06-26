import re
import json
import time
from openai import OpenAI
from config import OPENAI_API_KEY, BASE_URL, MODEL_NAME

client = OpenAI(
    base_url=BASE_URL,
    api_key=OPENAI_API_KEY
)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    print("email validation function called")
    return bool(re.match(pattern, email))

def validate_phone(phone):
    print("phone validation function called")
    pattern = r'^\d{10}$'
    return bool(re.match(pattern, phone))

def validate_password(password):
    print("password validation function called")
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return bool(re.match(pattern, password))

def validate_json_schema(data, schema):
    print("json schema validation function called")
    print("Data:", data)
    print("Schema:", schema)
    
    # Validate data against a JSON schema
    errors = []
    
    def validate_type(value, expected_type):
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "array":
            return isinstance(value, list)
        elif expected_type == "object":
            return isinstance(value, dict) and value is not None and not isinstance(value, list)
        return False
    
    def check_required(data, required):
        return [field for field in required if field not in data]
    
    def validate_field(value, field_schema, field_name):
        field_errors = []
        
        # Check type
        if field_schema and "type" in field_schema:
            if not validate_type(value, field_schema["type"]):
                field_errors.append(f"{field_name} should be of type {field_schema['type']}")
        
        # Check required
        if field_schema and field_schema.get("required", False) and (value is None or value == ""):
            field_errors.append(f"{field_name} is required")
        
        # Check minimum/maximum for numbers
        if field_schema and field_schema.get("type") == "number":
            if "minimum" in field_schema and value < field_schema["minimum"]:
                field_errors.append(f"{field_name} must be at least {field_schema['minimum']}")
            if "maximum" in field_schema and value > field_schema["maximum"]:
                field_errors.append(f"{field_name} must be at most {field_schema['maximum']}")
        
        # Check minLength/maxLength for strings
        if field_schema and field_schema.get("type") == "string":
            if "minLength" in field_schema and len(value) < field_schema["minLength"]:
                field_errors.append(f"{field_name} must be at least {field_schema['minLength']} characters")
            if "maxLength" in field_schema and len(value) > field_schema["maxLength"]:
                field_errors.append(f"{field_name} must be at most {field_schema['maxLength']} characters")
        
        return field_errors
    
    # Ensure schema is an object
    if not schema or not isinstance(schema, dict):
        return {
            "is_valid": False,
            "errors": ["Invalid schema: schema must be an object"],
            "message": "Validation failed"
        }
    
    # Check required fields
    if "required" in schema and isinstance(schema["required"], list):
        missing = check_required(data, schema["required"])
        if missing:
            errors.extend([f"Missing required field: {field}" for field in missing])
    
    # Validate each field
    properties = schema.get("properties", {})
    for field_name, field_schema in properties.items():
        if field_name in data:
            errors.extend(validate_field(data[field_name], field_schema, field_name))
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "message": "Valid data" if len(errors) == 0 else "Validation failed"
    }

def validate_date_format(date, format_str):
    print("date format validation function called")
    print("Date:", date)
    print("Format:", format_str)
    
    # If no format is provided, use a default format
    if not format_str:
        format_str = "YYYY-MM-DD"
    
    # Convert format to regex pattern
    def format_to_regex(format_pattern):
        return (format_pattern
                .replace("YYYY", r"\d{4}")
                .replace("MM", r"(0[1-9]|1[0-2])")
                .replace("DD", r"(0[1-9]|[12]\d|3[01])")
                .replace("HH", r"([01]\d|2[0-3])")
                .replace("mm", r"([0-5]\d)")
                .replace("ss", r"([0-5]\d)"))
    
    pattern = re.compile(f"^{format_to_regex(format_str)}$")
    return bool(pattern.match(date))

def validate_ip_address(ip):
    print("ip address validation function called")
    ipv4_pattern = r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    return bool(re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip))

def execute_function_call(func_name, args):
    if func_name == "validate_email":
        return validate_email(args["email"])
    elif func_name == "validate_phone":
        return validate_phone(args["phone"])
    elif func_name == "validate_password":
        return validate_password(args["password"])
    elif func_name == "validate_json_schema":
        return validate_json_schema(json.loads(args["data"]), json.loads(args["schema"]))
    elif func_name == "validate_date_format":
        return validate_date_format(args["date"], args["format"])
    elif func_name == "validate_ip_address":
        return validate_ip_address(args["ip"])
    else:
        raise ValueError(f"Unknown function: {func_name}")

tools = [{
    "type": "function",
    "name": "validate_email",
    "description": "validate an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "the email address needed to validate",
            }
        },
        "required": ["email"],
        "additionalProperties": False,
    }
}, {
    "type": "function",
    "name": "validate_phone",
    "description": "validate a phone number",
    "parameters": {
        "type": "object",
        "properties": {
            "phone": {
                "type": "string",
                "description": "the phone number needed to validate"
            }
        },
        "required": ["phone"],
        "additionalProperties": False,
    }
}, {
    "type": "function",
    "name": "validate_password",
    "description": "validate a password",
    "parameters": {
        "type": "object",
        "properties": {
            "password": {
                "type": "string",
                "description": "the password needed to validate"
            }
        },
        "required": ["password"],
        "additionalProperties": False,
    }
}, {
    "type": "function",
    "name": "validate_json_schema",
    "description": "validate a given json data against a given json schema",
    "parameters": {
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "the json data needed to validate"
            },
            "schema": {
                "type": "string",
                "description": "the json schema needed to validate"
            }
        },
        "required": ["data", "schema"],
        "additionalProperties": False,
    }
}, {
    "type": "function",
    "name": "validate_date_format",
    "description": "validate a given date against a given date format",
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "the date needed to validate"
            },
            "format": {
                "type": "string",
                "description": "the date format used to validate the given date"
            }
        },
        "required": ["date", "format"],
    }
}, {
    "type": "function",
    "name": "validate_ip_address",
    "description": "validate an ip address",
    "parameters": {
        "type": "object",
        "properties": {
            "ip": {
                "type": "string",
                "description": "the ip address needed to validate"
            }
        },
        "required": ["ip"],
        "additionalProperties": False,
    }
}]

def function_call_playground_validation(prompt):
    messages = [{
        "role": "system",
        "content": "You are a validation assistant. You can validate emails, phone numbers, passwords, JSON schemas, date formats, and IP addresses. When asked to validate something, respond with a JSON object containing the validation type and the value to validate. For example: {\"type\": \"email\", \"value\": \"test@example.com\"}. For JSON schema validation, use format: {\"type\": \"json_schema\", \"data\": {...}, \"schema\": {...}}. For phone numbers, use type: \"phone\". For date format validation, use format: {\"type\": \"date_format\", \"date\": \"2023-12-31\", \"format\": \"YYYY-MM-DD\"}"
    }, {
        "role": "user",
        "content": prompt
    }]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.01,
            stream=False,
            top_p=0.95,
            response_format={"type": "json_object"}
        )

        response_content = json.loads(response.choices[0].message.content)
        print("API Response:", response_content)

        validation_result = None
        if response_content["type"] == "email":
            validation_result = validate_email(response_content["value"])
        elif response_content["type"] in ["phone", "phone_number"]:
            validation_result = validate_phone(response_content["value"])
        elif response_content["type"] == "password":
            validation_result = validate_password(response_content["value"])
        elif response_content["type"] == "json_schema":
            data = json.loads(response_content["data"]) if isinstance(response_content["data"], str) else response_content["data"]
            schema = json.loads(response_content["schema"]) if isinstance(response_content["schema"], str) else response_content["schema"]
            validation_result = validate_json_schema(data, schema)
        elif response_content["type"] == "date_format":
            validation_result = validate_date_format(
                response_content.get("date", response_content.get("value")),
                response_content["format"]
            )
        elif response_content["type"] == "ip_address":
            validation_result = validate_ip_address(response_content["value"])
        else:
            raise ValueError(f"Unknown validation type: {response_content['type']}")

        return json.dumps({
            "type": response_content["type"],
            "value": response_content.get("value", response_content.get("data", response_content.get("date"))),
            "isValid": validation_result
        })
    except Exception as error:
        print("API Error:", {
            "status": getattr(error, 'status', None),
            "message": str(error),
            "type": getattr(error, 'type', None),
            "headers": getattr(error, 'headers', None),
            "response": getattr(error, 'response', {}).get('data', None) if hasattr(error, 'response') else None
        })
        raise error

prompts = [
    "Validate this email address: user@example.com",
    "Validate this phone number: +1-555-123-4567",
    "Validate this password: Password123!",
    "Validate this data against the schema: {'name': 'John', 'age': 30} with schema {'type': 'object', 'properties': {'name': {'type': 'string'}, 'age': {'type': 'number', 'minimum': 0, 'maximum': 120}}, 'required': ['name', 'age']}",
    "Validate this date format: 2023-12-31",
    "Validate this IP address: 192.168.1.1"
]

total_time = 0
for p in prompts:
    start = time.time() * 1000  # Convert to milliseconds like JavaScript
    result = function_call_playground_validation(p)
    end = time.time() * 1000
    total_time += (end - start)
    print(f"Prompt: {p}")
    print(f"Result: {result}")
    print(f"Time taken: {(end-start)/1000} seconds")
    print("--------------------------------")
print(f"Total time taken: {total_time/1000} seconds")
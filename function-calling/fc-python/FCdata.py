import os
import json
import time
from datetime import datetime
import csv
import io
from typing import List, Dict, Any, Union
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME

client = OpenAI(api_key=OPENAI_API_KEY)

def csv_to_json(csv_data: str) -> str:
    """Convert CSV data to JSON format."""
    try:
        # Create a CSV reader from the string
        csv_file = io.StringIO(csv_data)
        csv_reader = csv.DictReader(csv_file)
        
        # Convert to list of dictionaries
        data = list(csv_reader)
        
        # Convert to JSON string
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error converting CSV to JSON: {str(e)}"

def json_to_csv(json_data: str) -> str:
    """Convert JSON data to CSV format."""
    try:
        # Parse JSON string
        data = json.loads(json_data)
        
        if not data:
            return "Error: Empty JSON data"
        
        # Get headers from first item
        headers = list(data[0].keys())
        
        # Create CSV string
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        
        # Write headers and data
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    except Exception as e:
        return f"Error converting JSON to CSV: {str(e)}"

def filter_data(data: str, condition: str) -> str:
    """Filter data based on a condition."""
    try:
        # Parse JSON data
        items = json.loads(data)
        
        # Create a filter function from the condition
        filter_func = eval(f"lambda x: {condition}")
        
        # Apply filter
        filtered_items = list(filter(filter_func, items))
        
        return json.dumps(filtered_items, indent=2)
    except Exception as e:
        return f"Error filtering data: {str(e)}"

def sort_data(data: str, key: str, reverse: bool = False) -> str:
    """Sort data by a specified key."""
    try:
        # Parse JSON data
        items = json.loads(data)
        
        # Sort items
        sorted_items = sorted(items, key=lambda x: x[key], reverse=reverse)
        
        return json.dumps(sorted_items, indent=2)
    except Exception as e:
        return f"Error sorting data: {str(e)}"

def aggregate_data(data: str, operation: str, field: str) -> str:
    """Perform aggregation operations on data."""
    try:
        # Parse JSON data
        items = json.loads(data)
        
        # Extract values for the specified field
        values = [item[field] for item in items]
        
        # Perform operation
        if operation.lower() == "average":
            result = sum(values) / len(values)
        elif operation.lower() == "sum":
            result = sum(values)
        elif operation.lower() == "min":
            result = min(values)
        elif operation.lower() == "max":
            result = max(values)
        else:
            return f"Error: Unsupported operation '{operation}'"
        
        return json.dumps({"operation": operation, "field": field, "result": result}, indent=2)
    except Exception as e:
        return f"Error aggregating data: {str(e)}"

# Define the tools available to the model
tools = [
    {
        "name": "csv_to_json",
        "description": "Convert CSV data to JSON format",
        "parameters": {
            "type": "object",
            "properties": {
                "csv_data": {
                    "type": "string",
                    "description": "The CSV data to convert"
                }
            },
            "required": ["csv_data"]
        }
    },
    {
        "name": "json_to_csv",
        "description": "Convert JSON data to CSV format",
        "parameters": {
            "type": "object",
            "properties": {
                "json_data": {
                    "type": "string",
                    "description": "The JSON data to convert"
                }
            },
            "required": ["json_data"]
        }
    },
    {
        "name": "filter_data",
        "description": "Filter data based on a condition",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "The JSON data to filter"
                },
                "condition": {
                    "type": "string",
                    "description": "The condition to filter by (e.g., 'age > 25')"
                }
            },
            "required": ["data", "condition"]
        }
    },
    {
        "name": "sort_data",
        "description": "Sort data by a specified key",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "The JSON data to sort"
                },
                "key": {
                    "type": "string",
                    "description": "The key to sort by"
                },
                "reverse": {
                    "type": "boolean",
                    "description": "Whether to sort in descending order",
                    "default": False
                }
            },
            "required": ["data", "key"]
        }
    },
    {
        "name": "aggregate_data",
        "description": "Perform aggregation operations on data",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "The JSON data to aggregate"
                },
                "operation": {
                    "type": "string",
                    "description": "The operation to perform (average, sum, min, max)",
                    "enum": ["average", "sum", "min", "max"]
                },
                "field": {
                    "type": "string",
                    "description": "The field to aggregate"
                }
            },
            "required": ["data", "operation", "field"]
        }
    }
]

def function_call_playground(prompt: str) -> str:
    """Process a prompt and execute the appropriate function call."""
    try:
        # Get completion from OpenAI
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            tools=tools,
            tool_choice="auto"
        )
        
        # Get the function call
        message = response.choices[0].message
        
        if not message.tool_calls:
            return "No function call was made in response to the prompt."
        
        # Process each tool call
        results = []
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            # Execute the appropriate function
            if function_name == "csv_to_json":
                result = csv_to_json(function_args["csv_data"])
            elif function_name == "json_to_csv":
                result = json_to_csv(function_args["json_data"])
            elif function_name == "filter_data":
                result = filter_data(function_args["data"], function_args["condition"])
            elif function_name == "sort_data":
                result = sort_data(
                    function_args["data"],
                    function_args["key"],
                    function_args.get("reverse", False)
                )
            elif function_name == "aggregate_data":
                result = aggregate_data(
                    function_args["data"],
                    function_args["operation"],
                    function_args["field"]
                )
            else:
                result = f"Unknown function: {function_name}"
            
            results.append(result)
        
        return "\n".join(results)
    
    except Exception as e:
        return f"Error in function_call_playground: {str(e)}"

if __name__ == "__main__":
    # Test prompts
    test_prompts = [
        "Convert this CSV data to JSON: name,age,city\nJohn,30,New York\nJane,25,Los Angeles",
        "Convert this JSON to CSV: [{\"name\":\"John\",\"age\":30,\"city\":\"New York\"},{\"name\":\"Jane\",\"age\":25,\"city\":\"Los Angeles\"}]",
        "Filter this data to show only people over 25: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
        "Sort this data by age in descending order: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]",
        "Calculate the average age from this data: [{\"name\":\"John\",\"age\":30},{\"name\":\"Jane\",\"age\":25},{\"name\":\"Bob\",\"age\":35}]"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        print("Response:", function_call_playground(prompt))
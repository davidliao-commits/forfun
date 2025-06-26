import math
import os
import json
import time
from openai import OpenAI
import sys
import requests
import sympy
from config import OPENAI_API_KEY, BASE_URL, MODEL_NAME

client = OpenAI(
    base_url="https://api.siliconflow.cn/v1",
    api_key="sk-wosxiisuzqcpwbnmaobpgflmgxzpumvxsuvusoduscvhcdoc"
)
print("client started")

def add(a:float, b:float):
    print("addition function called")
    return a+b

def subtract(a:float, b:float):
    print("subtraction function called")
    return a-b

def multiply(a:float, b:float):
    print("multiplication function called")
    return a*b

def divide(a:float, b:float):
    print("division function called")
    if b==0:
        return "Error: Division by zero"
    return a/b

def sqrt(a:float):
    print("square root function called")
    return math.sqrt(a);

def derivative(func:str, x:float):
    print("derivative function called")
    try:
        expr=sympy.sympify(func)
        return sympy.diff(expr,x)
    except Exception as e:
        return f"Error: {str(e)}"

def integrate(func:str, x:float):
    print("integration function called")
    try:
        expr=sympy.sympify(func)
        return sympy.integrate(expr,x)
    except Exception as e:
        return f"Error: {str(e)}"

# def solve_equation(equation:str, variable:str):
#     try:
#         expr=sympy.sympify(equation)
#         return sympy.solve(expr,variable)
#     except Exception as e:
#         return f"Error:{str(e)}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "add two numbers together",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "first number"
                    },
                    "b": {
                        "type": "number",
                        "description": "second number"
                    }
                },
                "required": ["a", "b"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "subtract",
            "description": "subtract two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "first number"
                    },
                    "b": {
                        "type": "number",
                        "description": "second number"
                    }
                },
                "required": ["a", "b"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "multiply",
            "description": "multiply two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "first number"
                    },
                    "b": {
                        "type": "number",
                        "description": "second number"
                    }
                },
                "required": ["a", "b"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "divide",
            "description": "divide two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "first number"
                    },
                    "b": {
                        "type": "number",
                        "description": "second number"
                    }
                },
                "required": ["a", "b"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "derivative",
            "description": "compute the derivative of a function",
            "parameters": {
                "type": "object",
                "properties": {
                    "func": {
                        "type": "string",
                        "description": "the function to be differentiated"
                    },
                    "x": {
                        "type": "number",
                        "description": "the variable to differentiate with respect to"
                    }
                },
                "required": ["func", "x"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "integrate",
            "description": "compute the integral of a function",
            "parameters": {
                "type": "object",
                "properties": {
                    "func": {
                        "type": "string",
                        "description": "the function to be integrated"
                    },
                    "x": {
                        "type": "number",
                        "description": "the variable of integration"
                    }
                },
                "required": ["func", "x"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sqrt",
            "description": "compute the square root of a number",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "the number to compute the square root of"
                    }
                },
                "required": ["a"],
                "additionalProperties": False
            }
        }
    }
]

def function_call_playground(prompt: str):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a mathematical assistant. When solving equations or expressions, "
                    "you must call appropriate functions from this list: add, subtract, multiply, divide, "
                    "derivative, integrate, sqrt. For each mathematical operation, you must use the corresponding function. "
                    "For example, if asked to add numbers, use the add function. If asked to find a square root, use the sqrt function. "
                    "Always use the functions provided rather than calculating directly."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            }
        ]

        response = client.chat.completions.create(
            model="Qwen/Qwen3-8B",
            messages=messages,
            temperature=0.01,
            stream=False,
            top_p=0.95,
            tools=tools,
           # tool_choice="required"
        )

        # Check if the response has tool calls
        if not response.choices[0].message.tool_calls:
            # If no tool calls, try to parse the response and create appropriate function calls
            content = response.choices[0].message.content.lower()
            print(f'content: {content}')
            result = None
            
            if "sum" in content or "add" in content:
                # Extract numbers from the prompt
                import re
                numbers = re.findall(r'\d+', prompt)
                if len(numbers) >= 2:
                    result = add(float(numbers[0]), float(numbers[1]))
            elif "minus" in content or "subtract" in content:
                numbers = re.findall(r'\d+', prompt)
                if len(numbers) >= 2:
                    result = subtract(float(numbers[0]), float(numbers[1]))
            elif "times" in content or "multiply" in content:
                numbers = re.findall(r'\d+', prompt)
                if len(numbers) >= 2:
                    result = multiply(float(numbers[0]), float(numbers[1]))
            elif "divide" in content or "divided by" in content:
                numbers = re.findall(r'\d+', prompt)
                if len(numbers) >= 2:
                    result = divide(float(numbers[0]), float(numbers[1]))
            elif "derivative" in content:
                # Extract function and variable
                func_match = re.search(r'derivative of (.*?), where', prompt)
                if func_match:
                    func = func_match.group(1)
                    result = derivative(func, 0)  # Default x=0 for symbolic derivative
            elif "integral" in content or "integrate" in content:
                func_match = re.search(r'integral of (.*?), where', prompt)
                if func_match:
                    func = func_match.group(1)
                    result = integrate(func, 0)  # Default x=0 for symbolic integral
            elif "square root" in content or "sqrt" in content:
                numbers = re.findall(r'\d+', prompt)
                if numbers:
                    result = sqrt(float(numbers[0]))
            
            if result is not None:
                return f"The result is: {result}"
            return "Could not determine the appropriate mathematical operation to perform."

        # Process each tool call
        results = []
        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_out = None

            if function_name == "add":
                function_out = add(function_args["a"], function_args["b"])
            elif function_name == "subtract":
                function_out = subtract(function_args["a"], function_args["b"])
            elif function_name == "multiply":
                function_out = multiply(function_args["a"], function_args["b"])
            elif function_name == "divide":
                function_out = divide(function_args["a"], function_args["b"])
            elif function_name == "derivative":
                function_out = derivative(function_args["func"], function_args["x"])
            elif function_name == "integrate":
                function_out = integrate(function_args["func"], function_args["x"])
            elif function_name == "sqrt":
                function_out = sqrt(function_args["a"])

            if function_out is not None:
                results.append(function_out)
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call]
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(function_out)
                })

        # Get final response after all tool calls
        final_response = client.chat.completions.create(
            model="Qwen/Qwen3-8B",
            messages=messages,
            temperature=0.01,
            stream=False,
            top_p=0.95
        )

        if results:
            return f"The result is: {results[-1]}"  # Return the last result
        return final_response.choices[0].message.content

    except Exception as e:
        return f"Error in function_call_playground: {str(e)}"

prompt=[]
prompt.append("what is the sum of 1 and 2")
prompt.append("what is the value of 2 minus 1")
prompt.append("what is the value of 3 times 4")
prompt.append("what is the value of 70 divided by 5")
prompt.append("what is the derivative of 3*x, where x= 3")
prompt.append("what is the intergal of 3*x, where x=3")
prompt.append("solve for x in equation x squared plus 2x plus 1 equals 0")
prompt.append("solve for x in equation x squared equals 16")

import time

for p in prompt:
    start_time=time.time()
    print(function_call_playground(p))
    end_time=time.time()
    print(f"prompt:{p} time: {end_time-start_time}")
    
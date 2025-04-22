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
    base_url=BASE_URL,
    api_key=OPENAI_API_KEY
)
print("client started")

def add(a:float, b:float):
    return a+b

def subtract(a:float, b:float):
    return a-b

def multiply(a:float, b:float):
    return a*b

def divide(a:float, b:float):
    if b==0:
        return "Error: Division by zero"
    return a/b

def derivative(func:str, x:float):
    try:
        expr=sympy.sympify(func)
        return sympy.diff(expr,x)
    except Exception as e:
        return f"Error: {str(e)}"

def integrate(func:str, x:float):
    try:
        expr=sympy.sympify(func)
        return sympy.integrate(expr,x)
    except Exception as e:
        return f"Error: {str(e)}"

def solve_equation(equation:str, variable:str):
    try:
        expr=sympy.sympify(equation)
        return sympy.solve(expr,variable)
    except Exception as e:
        return f"Error:{str(e)}"

tools=[{
    "type":"function",
    "function":{
        "name":"add",
        "description":"add two numbers together",
        "parameters":{
            "type":"object",
            "properties":{
                "a":{
                    "type":"number",
                    "description":"first number"
                },
                "b":{
                    "type":"number",
                    "description":"second number"
                }
            },
            "required":["a","b"],
            "additionalProperties":False
        }

    },
    "type":"function",
    "function":{
        "name":"subtract",
        "description":"subtract two numbers",
        "parameters":{
            "type":"object",
            "properties":{
                "a":{
                    "type":"number",
                    "description":"first number"
                },
                "b":{
                    "type":"number",
                    "description":"second number"
                }
            },
            "required":["a","b"],
            "additionalProperties":False
        }
    },
    "type":"function",
    "function":{
        "name":"multiply",
        "description":"multiply two numbers",
        "parameters":{
            "type":"object",
            "properties":{
                "a":{
                    "type":"number",
                    "description":"first number"
                },
                "b":{
                    "type":"number",
                    "description":"second number"
                }
            },
            "required":["a","b"],
            "additionalProperties":False
        }
    },
    "type":"function",
    "function":{
        "name":"divide",
        "description":"divide two numbers",
        "parameters":{
            "type":"object",
            "properties":{
                "a":{
                    "type":"number",
                    "description":"first number"
                },
                "b":{
                    "type":"number",
                    "description":"second number"
                }
            },
            "required":["a","b"],
            "additionalProperties":False
        }
    },
    "type":"function",
    "function":{
        "name":"derivative",
        "description":"compute the derivative of a function",
        "parameters":{
            "type":"object",
            "properties":{
                "func":{
                    "type":"string",
                    "description":"the function to be differentiated"
                },
                "x":{
                    "type":"number",
                    "description":"the variable to differentiate with respect to"
                }
            },
            "required":["func","x"],
            "additionalProperties":False
        }
    },
    "type":"function",
    "function":{
        "name":"integrate",
        "description":"compute the integral of a function",
        "parameters":{
            "type":"object",
            "properties":{
                "func":{
                    "type":"string",
                    "description":"the function to be integrated"
                },
                "x":{
                    "type":"number",
                    "description":"the variable of integration"
                }
            },
            "required":["func","x"],
            "additionalProperties":False
        }
    },
    "type":"function",
    "function":{
        "name":"solve_equation",
        "description":"solve an equation for a given variable",
        "parameters":{
            "type":"object",
            "properties":{
                "equation":{
                    "type":"string",
                    "description":"the equation to solve"
                },
                "variable":{
                    "type":"string",
                    "description":"the variable to solve for"
                }
            },
            "required":["equation","variable"],
            "additionalProperties":False
        }
    }

    
}]

def function_call_playground(prompt:str):
    try:
        messages=[
             {"role":"system","content":prompt}
        ]

        response=client.chat.completions.create(
                model=MODEL_NAME,
            messages=messages,
            temperature=0.01,
            stream=False,
            top_p=0.95,
            tools=tools
        )

        # Check if the response has tool calls
        if not response.choices[0].message.tool_calls:
            return "No function call was made in response to the prompt."
            
        func1_name=response.choices[0].message.tool_calls[0].function.name
        func1_args=response.choices[0].message.tool_calls[0].function.arguments
        func1_out=eval(f'{func1_name}(**{func1_args})')

        messages.append(response.choices[0].message)
        messages.append({
            'role':'tool',
            'content':f'{func1_out}',
            'tool_call_id':response.choices[0].message.tool_calls[0].id
        })

        response=client.chat.completions.create(
                model=MODEL_NAME,
            messages=messages,
            temperature=0.01,
            stream=False,
            top_p=0.95,
            tools=tools
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error in function_call_playground: {str(e)}"

prompt=[]
prompt.append("what is the sum of 1 and 2")
prompt.append("what is the value of 2 minus 1")
prompt.append("what is the value of 3 times 4")
prompt.append("what is the value of 70 divided by 5")
prompt.append("what is the derivative of 3x, where x=3")
prompt.append("what is the intergal of 3x, where x=3")
prompt.append("solve equation for value of x squared plus 2x plus 1")

import time

for p in prompt:
    start_time=time.time()
    print(function_call_playground(p))
    end_time=time.time()
    print(f"prompt:{p} time: {end_time-start_time}")
    
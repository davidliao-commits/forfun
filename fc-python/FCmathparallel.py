import concurrent.futures
import json
import sympy
import math
import openai
from config import OPENAI_API_KEY, BASE_URL, MODEL_NAME
client=openai.OpenAI(
    base_url=BASE_URL,
    api_key=OPENAI_API_KEY
)
# Define all your math functions
def add(a: float, b: float):
    print("addition function called")
    return a + b
def subtract(a: float, b: float):
    print("subtraction function called")
    return a - b
def multiply(a: float, b: float):
    print("multiplication function called")
    return a * b
def divide(a: float, b: float):
    print("division function called")
    return "Error" if b == 0 else a / b
def sqrt(a: float):
    print("square root function called")
    return math.sqrt(a)
def derivative(func: str, x: float):
    print("derivative function called")
    try:
        expr = sympy.sympify(func)
        return str(sympy.diff(expr, sympy.Symbol('x')).subs(sympy.Symbol('x'), x))
    except Exception as e:
        return str(e)
def integrate(func: str, x: float):
    print("integration function called")
    try:
        expr = sympy.sympify(func)
        return str(sympy.integrate(expr, sympy.Symbol('x')).subs(sympy.Symbol('x'), x))
    except Exception as e:
        return str(e)

# Tool name to function mapping
available_functions = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "sqrt": sqrt,
    "derivative": derivative,
    "integrate": integrate,
}

# Simulate parallel function calling
def function_call_playground(prompt: str, client):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a math assistant. Given a question, always respond with a JSON array "
                    "of function calls (not explanations). Each function call should have a 'name' "
                    "and an 'arguments' field. Example:\n"
                    "[{\"name\": \"add\", \"arguments\": {\"a\": 2, \"b\": 3}},"
                    " {\"name\": \"multiply\", \"arguments\": {\"a\": 4, \"b\": 5}}]"
                )
            },
            {"role": "user", "content": prompt}
        ]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.01,
            stream=False,
            top_p=0.95
        )

        tool_call_json = response.choices[0].message.content.strip()

        # Try parsing JSON from model output
        try:
            tool_calls = json.loads(tool_call_json)
        except json.JSONDecodeError:
            return f"Invalid JSON output: {tool_call_json}"

        # Parallel execution
        results = {}

        def call_function(tc):
            name = tc["name"]
            args = tc["arguments"]
            if name in available_functions:
                return (name, available_functions[name](**args))
            else:
                return (name, f"Unknown function '{name}'")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(call_function, tc): tc["name"] for tc in tool_calls}
            for future in concurrent.futures.as_completed(futures):
                fname, result = future.result()
                results[fname] = result

        return results

    except Exception as e:
        return f"Error in function_call_playground: {str(e)}"

if __name__ == "__main__":
    try:
        # Test the function with a simple math problem
        prompt = "What is 2 + 3 and then multiply the result by 4?"
        print("Sending prompt:", prompt)
        result = function_call_playground(prompt, client)
        print("Result:", result)
    except Exception as e:
        print("Error in main execution:", str(e))

from openai import OpenAI
import requests
import json
import os
import sys
from config import OPENAI_API_KEY, BASE_URL, MODEL_NAME
from FCweather import function_call_playground


client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=BASE_URL
)
print("OpenAI client initialized")

def get_geo_location(city: str):
    """
    Get the latitude and longitude coordinates for a given city.
    Returns a tuple of (latitude, longitude) if successful, None if failed.
    """
    api_key = "your openweathermap api key"
    base_url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city,
        "appid": api_key
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                latitude = data[0]["lat"]
                longitude = data[0]["lon"]
                return {
                    "latitude": latitude,
                    "longitude": longitude,
                    "city": city,
                    "success": True
                }
        return {
            "success": False,
            "error": f"Could not find coordinates for {city}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting coordinates for {city}: {str(e)}"
        }

tools = [{
    "type": "function",
    "function": {
        "name": "get_geo_location",
        "description": "Get the latitude and longitude coordinates for a given city name",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The name of the city to get coordinates for"
                }
            },
            "required": ["city"],
            "additionalProperties": False
        }
    }
}]

def function_call_playground1(prompt: str):
    """
    Function call playground that chains geo location lookup with weather lookup.
    First gets coordinates for a city, then uses those coordinates to get the weather.
    """
    messages = [{
        "role": "system",
        "content": "You are a helpful assistant that can find the weather for any city. "
                  "First, get the coordinates of the city, then use those coordinates to get the weather. "
                  "If you encounter any errors, explain them clearly."
    }, {
        "role": "user",
        "content": prompt
    }]

    # First function call to get coordinates
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tools,
        temperature=0.01,
        stream=False,
        top_p=0.95,
        tool_choice="auto"
    )

    func1_name = response.choices[0].message.tool_calls[0].function.name
    func1_args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    func1_out = get_geo_location(**func1_args)

    # Add the results to the conversation
    messages.append(response.choices[0].message)
    messages.append({
        "role": "tool",
        "content": json.dumps(func1_out),
        "tool_call_id": response.choices[0].message.tool_calls[0].id
    })

    # If we got coordinates successfully, proceed to get weather
    if func1_out.get("success", False):
        # Create a new prompt for the weather function
        weather_prompt = f"What is the weather at coordinates {func1_out['latitude']} and {func1_out['longitude']} for {func1_out['city']}?"
        return function_call_playground(weather_prompt)
    else:
        return f"Error: {func1_out.get('error', 'Unknown error occurred')}"

# Example usage
if __name__ == "__main__":
    prompt = "What is the weather in Beijing?"
    import time
    start_time = time.time()
    result = function_call_playground1(prompt)
    end_time = time.time()
    print(f"\nResult: {result}")
    print(f"Time taken for function call playground: {end_time-start_time:.2f} seconds")
    
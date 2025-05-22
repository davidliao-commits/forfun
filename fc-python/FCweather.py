import openai
import json
from openai import OpenAI
import requests
import sys
from config import OPENAI_API_KEY, BASE_URL, MODEL_NAME


latitude=None
longtitude=None

    # Read API key
    # with open("api.txt", "r") as f:
    #     api_key = f.read().strip()
    # print("API key loaded successfully")
    
        # Initialize client with base URL
client = OpenAI(
    api_key="sk-wosxiisuzqcpwbnmaobpgflmgxzpumvxsuvusoduscvhcdoc",
    base_url="https://api.siliconflow.cn/v1"
)
print("OpenAI client initialized")

def get_weather( latitude: float, longtitude: float):
    api_key = "ff3f2807abcb8a97b30115d180fdde54"  # Replace with your actual OpenWeatherMap API key
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': latitude,
        'lon': longtitude,
        'appid': api_key
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']-273.15
        feels_like = data['main']['feels_like']-273.15
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        return f"The weather in coordinates {latitude} and {longtitude} is {weather} with a temperature of {temperature}celsius (feels like {feels_like}celsius), humidity {humidity}%, and wind speed {wind_speed} m/s"
    else:
        return f"Sorry, I could not retrieve the weather for coordinates {latitude} and {longtitude} at the moment"


def get_coordinates(city_name: str):
    print(f"getting coordinates for city:{city_name}")
    api_key="ff3f2807abcb8a97b30115d180fdde54"
    base_url="https://api.openweathermap.org/geo/1.0/direct"
    params={
        "q":city_name,
        "appid":api_key
    }
    
    response=requests.get(base_url,params=params)
    if response.status_code==200:
        data=response.json()
        if data:
            latitude=data[0]['lat']
            longtitude=data[0]['lon']
            latitude=float(latitude)
            longtitude=float(longtitude)
            return latitude,longtitude
        else:
            return None,None
        
    else:
        print(f"Error:{response.status_code}")
        return None,None
    


tools = [
    {
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'description': 'Get the weather for a given coordinates',
            'parameters': {
                'type': 'object',
                'properties': {
                    'latitude': {
                        'type': 'number',
                        'description': 'latitude of the location'
                    },
                    'longtitude': {
                        'type': 'number',
                        'description': 'longitude of the location'
                    }
                },
                'required': ['latitude', 'longtitude'],
                'additionalProperties': False
            }
        }
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_coordinates',
            'description': 'Get the coordinates of a given city name, eg: "New York"',
            'parameters': {
                'type': 'object',
                'properties': {
                    'city_name': {
                        'type': 'string',
                        'description': 'the name of the city provided by the user to fetch corresponding coordinates',
                    }
                },
                'required': ['city_name']
            }
        }
    }
]



def function_call_playground_coords(prompt: str):
    print("starting function call playground for coordinates")
    global latitude, longtitude
    messages = [
        {'role': 'system', 'content': prompt}
    ]
    response = client.chat.completions.create(
        model="THUDM/GLM-4-9B-0414",
        messages=messages,
        tools=tools,
        temperature=0.01,
        stream=False,
        top_p=0.95,
    )

    func_call = response.choices[0].message.tool_calls[0]
    func1_name = func_call.function.name
    func1_args = json.loads(func_call.function.arguments)  # safer parsing
    func1_out = eval(f'{func1_name}(**{func1_args})')

    # Only set global vars if successful
    if func1_out and func1_out[0] is not None and func1_out[1] is not None:
        latitude, longtitude = func1_out
    else:
        print("Failed to retrieve coordinates.")
        latitude, longtitude = None, None

    messages.append(response.choices[0].message)
    messages.append({
        'role': 'tool',
        'content': f'Coordinates: {latitude}, {longtitude}',
        'tool_call_id': func_call.id
    })

    return f"Coordinates obtained: {latitude}, {longtitude}" if latitude is not None else "Failed to get coordinates."





def function_call_playground(prompt: str):
    print("starting function call playground for weather")
    global latitude, longtitude
    messages = [{"role": "system", "content": prompt}]

    response = client.chat.completions.create(
        model="THUDM/GLM-4-9B-0414",
        messages=messages,
        temperature=0.01,
        stream=False,
        top_p=0.95,
        tools=tools
    )

    tool_calls = response.choices[0].message.tool_calls

    if tool_calls is None:
        print("⚠️ No tool call was made by the model.")
        return "No tool call triggered."

    func_call = tool_calls[0]
    func_name = func_call.function.name
    func_args = json.loads(func_call.function.arguments)
    func_out = eval(f'{func_name}(**{func_args})')

    if func_name == 'get_coordinates':
        if func_out and func_out[0] is not None:
            latitude, longtitude = func_out
            result = f"Coordinates obtained: {latitude}, {longtitude}"
        else:
            result = "Failed to retrieve coordinates."
    elif func_name == 'get_weather':
        result = func_out  # Just a string message
    else:
        result = "Unknown function returned."

    messages.append(response.choices[0].message)
    messages.append({
        'role': 'tool',
        'content': str(func_out),
        'tool_call_id': func_call.id
    })

    final_response = client.chat.completions.create(
        model="THUDM/GLM-4-9B-0414",
        messages=messages,
        temperature=0.01,
        stream=False,
        top_p=0.95,
        tools=tools
    )

    return final_response.choices[0].message.content or result


prompt1="what are the coordinates of Zurich, Switzerland?"

import time
start_time=time.time()

# First get coordinates
print(function_call_playground_coords(prompt1))
print(f"coordinates:{latitude},{longtitude}")
# Then get weather using the stored coordinates
if latitude is not None and longtitude is not None:
    prompt2 = f"What is the weather like in coordinates {latitude}, {longtitude} today?"
    print(function_call_playground(prompt2))
else:
    print("No weather request made due to missing coordinates.")


end_time=time.time()
print(f"Execution time:{end_time-start_time} seconds")
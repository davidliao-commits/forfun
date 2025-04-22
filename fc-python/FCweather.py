import openai
import json
from openai import OpenAI
import requests
import sys
from config import OPENAI_API_KEY, BASE_URL, MODEL_NAME

    # Read API key
    # with open("api.txt", "r") as f:
    #     api_key = f.read().strip()
    # print("API key loaded successfully")
    
        # Initialize client with base URL
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=BASE_URL
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


tools = [{
    'type': 'function',
    'function':{
        'name':'get_weather',
        'description':'Get the weather for a given coordinates',
        'parameters':{
            'type':'object',
            'properties':{
                # 'location':{
                #     'type':'string',
                #     'description':'City name followed by country name e.g. Zurich, Switzerland'
                # },
                'latitude':{
                    'type':'number',
                    'description':'latitude of the location'
                },
                'longtitude':{
                    'type':'number',
                    'description':'following latitude coordinate, longitutude of the location'
                }
            },
            'required':['latitude','longtitude'],
            'additionalProperties':False
        },
    }
}]

print("Making API call...")
def function_call_playground(prompt:str):
    messages=[
        {"role": "system", "content": prompt}
    ]

    response=client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.01,
        stream=False,
        top_p=0.95,
        tools=tools
    )

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
prompt="What is the weather like in coordinates 47.3769 and 8.5417, today?"
import time
start_time=time.time()


print(function_call_playground(prompt))

end_time=time.time()
print(f"Execution time:{end_time-start_time} seconds")
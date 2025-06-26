import openai
import json
from openai import OpenAI
import requests
import sys
from config import OPENAI_API_KEY, BASE_URL, MODEL_NAME

client = OpenAI(
    api_key="sk-wosxiisuzqcpwbnmaobpgflmgxzpumvxsuvusoduscvhcdoc",
    base_url="https://api.siliconflow.cn/v1"
)
print("openai client initialized")
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
            return latitude,longtitude
        else:
            return None,None
        
    else:
        print(f"Error:{response.status_code}")
        return None,None
    


tools=[{
    'type' : 'function',
    'function':{
        'name':'get_coordinates',
        'description':'Get the coordinates of a given city name, eg :" New York"',
        'parameters':{
            'type':'object',
            'properties':{
                'type':'string',
                'name':'city_name',
                'description':'The name of the city to get corresponding latitude and longtitude for'
            }
        },
        'required':['city_name']
    }
}]


def function_call_playground_coords(prompt:str):
    print("starting function call playground")
    messages=[
        {'role':'system',
         'content':prompt
         }
    ]
    response=client.chat.completions.create(
        model="THUDM/GLM-4-9B-0414",
        messages=messages,
        tools=tools,
        temperature=0.01,
        stream=False,
        top_p=0.95,
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
        model="THUDM/GLM-4-9B-0414",
        messages=messages,
        tools=tools,
        temperature=0.01,
        stream=False,
        top_p=0.95,
    )

    return response.choices[0].message.content
prompt="what are the coordinates of Abu Dhabi"
import time
start_time=time.time()

print(function_call_playground_coords(prompt))

end_time=time.time()
print(f"Time taken: {end_time-start_time} seconds")
    
    
    
   

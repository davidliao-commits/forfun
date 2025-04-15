from openai import OpenAI
import json
import os
import sys
import requests
import time


client = OpenAI(
    api_key="sk-wosxiisuzqcpwbnmaobpgflmgxzpumvxsuvusoduscvhcdoc",
    base_url="https://api.siliconflow.cn"
)


print("OpenAi client initialized.")

def get_definition(word:str):
    print(f"Getting definition for {word}")
    url = "https://urban-dictionary7.p.rapidapi.com/v0/define"
    
    querystring = {"term": word}
    
    headers = {
        "x-rapidapi-key": "a9f051cf53msh70504d662074c20p10960fjsn413232e29f01",
        "x-rapidapi-host": "urban-dictionary7.p.rapidapi.com"
    }
    
    # Make the request exactly like in def_test.py
    response = requests.get(url, headers=headers, params=querystring)
    
    # Process the response
    if response.status_code == 200:
        data = response.json()
        definition = data['list'][0]['definition']
        # breakpoint()
        return f"The definition of {word} is {definition}"
    else:
        print(f"Error: HTTP {response.status_code} - {response.text}")
        return f"Error: HTTP {response.status_code}"

tools=[{
    'type':'function',
    'function': {
        'name':'get_definition',
        'description':'Get the definition of a word',
        'parameters':{
            'type':'object',
            'properties':{
                'word':{
                    'type':'string',
                    'description':'The word to get the definition of'
                }
            },
            'required':['word']
        }
    }
}]

print("Making API call...")
def function_call_playground(prompt:str):
    messages=[
        {
        "role":"system",
         "content":prompt
         }
    ]
    response=client.chat.completions.create(
         model="THUDM/glm-4-9b-chat",
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
          model="THUDM/glm-4-9b-chat",
        messages=messages,
        temperature=0.01,
        stream=False,
        top_p=0.95,
        tools=tools
    )
    # breakpoint()
    return response.choices[0].message.content

# Fix the prompt - it's missing a closing quote
prompt="what is the definition of the word 'nice'"

import time
start_time=time.time()
print(function_call_playground(prompt))
end_time=time.time()
print(f"time taken:{end_time-start_time}seconds")

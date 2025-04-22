import requests
import sys
try:
    r=requests.get("http://api.openai.com/v1/models")
    print("Status code:", r.status_code)
    print("Response:", r.text)

except requests.exceptions.RequestException as e:
    print("connection failed:", e)
    


import os
from dotenv import load_dotenv
import openai
import requests

# Load environment variables
load_dotenv()

# Print environment variables
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
print(f"MODEL_NAME: {os.getenv('MODEL_NAME')}")
print(f"BASE_URL: {os.getenv('BASE_URL')}")

# Test OpenAI client
client = openai.OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('BASE_URL')
)

print("OpenAI client initialized successfully")

# Test requests
response = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=39.90872&lon=116.4075&appid=ff3f2807abcb8a97b30115d180fdde54")
print(f"Weather API response status: {response.status_code}") 
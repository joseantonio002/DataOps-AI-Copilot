import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
    "Content-Type": "application/json"
}

payload = {
    "model": "qwen/qwen3.8-27b",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpulf and concise assistant"
        },
        {
            "role": "user",
            "content": "Say Hi"
        }
    ],
    "reasoning_effort": "low",
    "max_completion_tokens": 100
}

response = requests.post(url, headers=headers, 
                         json=payload, timeout=15)

response.raise_for_status()

data = response.json()

print(data["choices"][0]["message"]["content"])
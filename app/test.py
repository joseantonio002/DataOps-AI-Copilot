import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict
from typing import Literal

load_dotenv()

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
    "Content-Type": "application/json"
}

class IncidentAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    severity: Literal["low", "medium", "high", "critical"]
    recommended_action: str
    confidence: float

incident = """
El sistema de validación de billetes lleva
25 minutos sin responder.
"""

payload = {
    "model": "qwen/qwen3.8-27b",
    "messages": [
        {
            "role": "system",
            "content": (
                "You are an incident analysis system. "
                "Analyze operational incidents, determine their severity, "
                "and recommend an appropriate action."
            )
        },
        {
            "role": "user",
            "content": incident
        }
    ],
    "reasoning_effort": "low",
    "max_completion_tokens": 100,
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "incident_analysis",
            "strict": True,
            "schema": IncidentAnalysis.model_json_schema()
        }
    },
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=30
)

if not response.ok:
    print(response.text)
    response.raise_for_status()


content = response.json()["choices"][0]["message"]["content"]

analysis = IncidentAnalysis.model_validate_json(content)

print(analysis)
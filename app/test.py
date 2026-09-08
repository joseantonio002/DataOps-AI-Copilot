import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict
from typing import Literal

load_dotenv()

url = "https://api.groq.com/openai/v1/chat/completions"

GROQ_API_KEY = os.getenv('GROQ_API_KEY', None)

if GROQ_API_KEY is None:
    raise Exception("Couldn't read GROQ_API_KEY")

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_incidents",
            "description": (
                "Retrieve individual transport incidents. "
                "Use this when the user wants to see, list, inspect, "
                "or filter specific incidents by line, severity or status."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "line": {
                        "type": ["string", "null"],
                        "description": "Transport line, e.g. L1, L2."
                    },
                    "severity": {
                        "type": ["string", "null"],
                        "enum": [
                            "low",
                            "medium",
                            "high",
                            "critical",
                            None
                        ]
                    },
                    "status": {
                        "type": ["string", "null"],
                        "description": "Incident status such as open or closed."
                    }
                },
                "required": ["line", "severity", "status"],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_incident_statistics",
            "description": (
                "Calculate aggregated incident statistics. "
                "Use this for counts, comparisons, trends, rankings "
                "or questions asking which line has more incidents."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "Number of previous days to analyze."
                    },
                    "lines": {
                        "type": ["array", "null"],
                        "items": {"type": "string"},
                        "description": (
                            "Lines to analyze. Null means all lines."
                        )
                    }
                },
                "required": ["days", "lines"],
                "additionalProperties": False
            }
        }
    }
]

class IncidentAnalysis(BaseModel):
    # Whether to ignore, allow, or forbid extra data during model initialization. Defaults to 'ignore'
    model_config = ConfigDict(extra="forbid")

    summary: str
    severity: Literal["low", "medium", "high", "critical"]
    recommended_action: str
    confidence: float

incident = """
Wich lines had the most incidents in the last month?
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
    "tools": tools,
    "tool_choice": "auto"
}

"""
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "incident_analysis",
            "strict": True,
            "schema": IncidentAnalysis.model_json_schema()
        }
    },
"""



response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=30
)

if not response.ok:
    print(response.text)
    response.raise_for_status()

#content = response.json()["choices"][0]["message"]["content"]

#analysis = IncidentAnalysis.model_validate_json(content)

print(response.json())
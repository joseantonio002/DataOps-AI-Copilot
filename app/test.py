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
                "Retrieve individual transport incidents from the database. "
                "Use this tool when the user wants to list, inspect, or filter "
                "specific incidents by transport line, severity, or status. "
                "Do not use this tool for aggregate counts, comparisons, or rankings."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "line": {
                        "type": ["string", "null"],
                        "enum": ["L1", "L2", "L3", None],
                        "description": (
                            "Transport line to filter by. "
                            "Use null when the user does not specify a line."
                        ),
                    },
                    "severity": {
                        "type": ["string", "null"],
                        "enum": [
                            "low",
                            "medium",
                            "high",
                            "critical",
                            None,
                        ],
                        "description": (
                            "Incident severity to filter by. "
                            "Use null when no severity filter is required."
                        ),
                    },
                    "status": {
                        "type": ["string", "null"],
                        "enum": [
                            "open",
                            "resolved",
                            None,
                        ],
                        "description": (
                            "Incident status to filter by. "
                            "Use null when no status filter is required."
                        ),
                    },
                },
                "required": [
                    "line",
                    "severity",
                    "status",
                ],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_incident_statistics",
            "description": (
                "Get aggregated incident counts grouped by transport line "
                "over a specified number of previous days, based on when incidents "
                "were opened. Use this tool for counts, comparisons, rankings, "
                "or questions about which line has more or fewer incidents. "
                "It can analyze all transport lines or only a selected subset. "
                "Do not use this tool when the user wants individual incident records."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "minimum": 1,
                        "description": (
                            "Number of previous days to include in the analysis. "
                            "For example, use 7 for the last 7 days."
                        ),
                    },
                    "lines": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "string",
                            "enum": ["L1", "L2", "L3"],
                        },
                        "uniqueItems": True,
                        "description": (
                            "Transport lines to include in the analysis. "
                            "Use null to analyze all lines. "
                            "For example, ['L1', 'L3'] compares only L1 and L3."
                        ),
                    },
                },
                "required": [
                    "days",
                    "lines",
                ],
                "additionalProperties": False,
            },
        },
    },
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
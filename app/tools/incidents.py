from pydantic import BaseModel
from typing import Literal
import sqlite3

class Incident(BaseModel):
    id: int
    line: str
    station: str
    severity: Literal["low", "medium", "high", "critical"]
    status: str
    description: str
    timestamp: str

class GetIncidentsResult(BaseModel):
    count: int
    incidents: list[Incident]

def get_incidents(
    line: str | None,
    severity: str | None,
    status: str | None
)-> GetIncidentsResult:
    pass
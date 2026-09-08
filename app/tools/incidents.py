from pydantic import BaseModel
from typing import Literal
from utils import CONFIG_PATH
import yaml
import sqlite3

def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)

class Incident(BaseModel):
    incident_id: str
    line: str
    station: str
    category: str
    severity: Literal["low", "medium", "high", "critical"]
    status: str
    opened_at: str
    resolved_at: str | None
    description: str

class GetIncidentsResult(BaseModel):
    count: int
    incidents: list[Incident]

def get_incidents(
    line: str | None,
    severity: str | None,
    status: str | None
)-> GetIncidentsResult:
    config = load_config()
    db_path = CONFIG_PATH.parent.parent / config["paths"]["data"] / config["db_name"]
    table_name = config["table_name"]

    query = f"SELECT incident_id, line, station, category, severity, status, opened_at, resolved_at, description FROM {table_name}"
    filters = []
    params: list[str] = []

    if line is not None:
        filters.append("line = ?")
        params.append(line)
    if severity is not None:
        filters.append("severity = ?")
        params.append(severity)
    if status is not None:
        filters.append("status = ?")
        params.append(status)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(query, params).fetchall()

    incidents = [Incident(**dict(row)) for row in rows]
    return GetIncidentsResult(count=len(incidents), incidents=incidents)

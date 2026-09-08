from pydantic import BaseModel
from utils import CONFIG_PATH
import yaml
import sqlite3


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


class LineIncidentCount(BaseModel):
    line: str
    count: int


class GetIncidentStatisticsResult(BaseModel):
    days: int
    total_incidents: int
    by_line: list[LineIncidentCount]


def get_incident_statistics(
    days: int,
    lines: list[str] | None = None
) -> GetIncidentStatisticsResult:
    if days <= 0:
        raise ValueError("days must be greater than 0")

    config = load_config()

    db_path = (
        CONFIG_PATH.parent.parent
        / config["paths"]["data"]
        / config["db_name"]
    )

    table_name = config["table_name"]

    query = f"""
        SELECT
            line,
            COUNT(*) AS count
        FROM {table_name}
        WHERE datetime(opened_at) >= datetime('now', ?)
    """

    params: list[str] = [f"-{days} days"]

    if lines is not None:
        if not lines:
            return GetIncidentStatisticsResult(
                days=days,
                total_incidents=0,
                by_line=[]
            )

        placeholders = ", ".join("?" for _ in lines)

        query += f"""
            AND line IN ({placeholders})
        """

        params.extend(lines)

    query += """
        GROUP BY line
        ORDER BY count DESC
    """

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(query, params).fetchall()

    by_line = [
        LineIncidentCount(
            line=row["line"],
            count=row["count"]
        )
        for row in rows
    ]

    total_incidents = sum(item.count for item in by_line)

    return GetIncidentStatisticsResult(
        days=days,
        total_incidents=total_incidents,
        by_line=by_line
    )



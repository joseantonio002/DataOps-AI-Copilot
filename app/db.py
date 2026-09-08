import sqlite3
import csv
from pathlib import Path

DB_NAME = "incidents.db"

db_path = Path(__file__).resolve().parent.parent

data_folder_path = db_path / "data"

db_path = data_folder_path / DB_NAME
csv_path = data_folder_path / "incidents.csv"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS incidents (
    incident_id TEXT PRIMARY KEY,
    line TEXT NOT NULL,
    station TEXT NOT NULL,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    opened_at TEXT NOT NULL,
    resolved_at TEXT,
    description TEXT NOT NULL
)
"""

DELETE_ALL = """
DELETE FROM incidents
"""

def load_incidents() -> None:
    with sqlite3.connect(db_path) as connection:
        cursor = connection.cursor()
        cursor.execute(CREATE_TABLE_SQL)
        cursor.execute(DELETE_ALL)

        with csv_path.open(newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            rows = [
                (
                    row["incident_id"],
                    row["line"],
                    row["station"],
                    row["category"],
                    row["severity"],
                    row["status"],
                    row["opened_at"],
                    row["resolved_at"] or None,
                    row["description"],
                )
                for row in reader
            ]

        cursor.executemany(
            """
            INSERT OR REPLACE INTO incidents (
                incident_id, line, station, category, severity, status,
                opened_at, resolved_at, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


if __name__ == "__main__":
    load_incidents()

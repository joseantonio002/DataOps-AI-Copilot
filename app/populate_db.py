import sqlite3
import csv
from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)


CONFIG = load_config()
DATA_FOLDER_PATH = PROJECT_ROOT / CONFIG["paths"]["data"]
DB_PATH = DATA_FOLDER_PATH / CONFIG["db_name"]
CSV_PATH = DATA_FOLDER_PATH / CONFIG["incidents_csv_name_file"]
TABLE_NAME = CONFIG["table_name"]

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS {table_name} (
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


def load_incidents() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(CREATE_TABLE_SQL.format(table_name=TABLE_NAME))

        with CSV_PATH.open(newline="", encoding="utf-8") as csv_file:
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
            f"""
            INSERT OR REPLACE INTO {TABLE_NAME} (
                incident_id, line, station, category, severity, status,
                opened_at, resolved_at, description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )


if __name__ == "__main__":
    load_incidents()

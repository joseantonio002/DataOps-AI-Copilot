from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd


random.seed(42)

LINES = ["L1", "L2", "L3"]

STATIONS = [
    "Central",
    "North",
    "South",
    "Airport",
    "University",
    "Harbour",
]

CATEGORIES = {
    "signal_failure": "Signalling system reported a technical failure",
    "delay": "Service running behind scheduled time",
    "door_failure": "Train door mechanism reported a failure",
    "overcrowding": "Passenger volume exceeded normal operating levels",
    "power_failure": "Electrical supply problem detected",
    "security": "Security incident reported by station staff",
    "maintenance": "Infrastructure unavailable due to maintenance",
}

SEVERITIES = ["low", "medium", "high", "critical"]


def generate_incidents(n: int = 200) -> pd.DataFrame:
    now = datetime(2026, 9, 7, 13, 0)

    incidents = []

    for i in range(1, n + 1):
        opened_at = now - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )

        severity = random.choices(
            SEVERITIES,
            weights=[30, 40, 20, 10],
        )[0]

        category = random.choice(list(CATEGORIES))

        status = random.choices(
            ["open", "resolved"],
            weights=[30, 70],
        )[0]

        if status == "resolved":
            resolution_minutes = random.randint(10, 300)
            resolved_at = opened_at + timedelta(minutes=resolution_minutes)
        else:
            resolved_at = None

        incidents.append(
            {
                "incident_id": f"INC-{i:04d}",
                "line": random.choice(LINES),
                "station": random.choice(STATIONS),
                "category": category,
                "severity": severity,
                "status": status,
                "opened_at": opened_at,
                "resolved_at": resolved_at,
                "description": CATEGORIES[category],
            }
        )

    return pd.DataFrame(incidents)


if __name__ == "__main__":
    df = generate_incidents()

    df.to_csv(
        "data/incidents.csv",
        index=False,
    )

    print(df.head())
    print(f"\nGenerated {len(df)} incidents")
import os
import uuid
from datetime import datetime, timedelta
from random import choice, randint

import clickhouse_connect
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = os.getenv("CLICKHOUSE_PORT", "8123")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "default")

ANIMALS = [
    "Lion",
    "Tiger",
    "Bear",
    "Elephant",
    "Giraffe",
    "Zebra",
    "Monkey",
    "Kangaroo",
    "Panda",
    "Fox",
]


def random_visit_time(start_date: datetime, end_date: datetime) -> datetime:
    delta = end_date - start_date
    random_days = randint(0, delta.days)
    return start_date + timedelta(days=random_days)


client = clickhouse_connect.get_client(
    host=CLICKHOUSE_HOST,
    port=CLICKHOUSE_PORT,
    username=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD,
    database=CLICKHOUSE_DB,
)

client.command(
    """
CREATE TABLE IF NOT EXISTS animal_visits (
    visitor_id UUID,
    animal_type String,
    visit_time DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toDate(visit_time)
ORDER BY (animal_type, visit_time)
"""
)


class Visit(BaseModel):
    visitor_id: str
    animal_type: str


@app.post("/visit/")
async def record_visit(visit: Visit):
    try:
        client.command(
            "INSERT INTO animal_visits (visitor_id, animal_type, visit_time) VALUES (%s, %s, %s)",
            (visit.visitor_id, visit.animal_type, datetime.now()),
        )
        return {"status": "Visit recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/popularity/")
async def animal_popularity():
    try:
        last_24_hours = datetime.now() - timedelta(hours=24)
        result = client.query(
            """
        SELECT animal_type, count() AS visits
        FROM animal_visits
        WHERE visit_time >= toDateTime(%s)
        GROUP BY animal_type
        ORDER BY visits DESC
        """,
            [last_24_hours],
        )

        popularity = [
            {"animal_type": row[0], "visits": row[1]} for row in result.result_rows
        ]
        return {"popularity": popularity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/peak_hours/")
async def peak_hours():
    try:
        last_24_hours = datetime.now() - timedelta(hours=24)
        result = client.query(
            """
        SELECT animal_type, toHour(visit_time) AS hour, count() AS visits
        FROM animal_visits
        WHERE visit_time >= toDateTime(%s)
        GROUP BY animal_type, hour
        ORDER BY animal_type, visits DESC
        """,
            [last_24_hours],
        )

        peak_hours = [
            {"animal_type": row[0], "hour": row[1], "visits": row[2]}
            for row in result.result_rows
        ]
        return {"peak_hours": peak_hours}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add_random_visits/")
async def add_random_visits(count: int):
    if count < 1:
        raise HTTPException(status_code=400, detail="Count must be greater than zero.")

    visits = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)

    for _ in range(count):
        visit = Visit(
            visitor_id=str(uuid.uuid4()),
            animal_type=choice(ANIMALS),
        )
        visits.append(visit)

        visit_time = random_visit_time(start_date, end_date)

        try:
            client.command(
                "INSERT INTO animal_visits (visitor_id, animal_type, visit_time) VALUES (%s, %s, %s)",
                (
                    visit.visitor_id,
                    visit.animal_type,
                    visit_time.strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        except Exception as e:
            return {"error": str(e)}

    return {"status": f"{count} visits recorded successfully", "visits": visits}

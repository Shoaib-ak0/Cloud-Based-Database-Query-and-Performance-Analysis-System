import statistics
import time

import mysql.connector
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.database import get_connection

router = APIRouter()

# Only allow known departments
ALLOWED_DEPARTMENTS = {
    "Engineering",
    "Marketing",
    "HR",
    "Finance",
    "Sales",
    "Operations",
    "IT",
    "Research"
}


class BenchmarkRequest(BaseModel):
    department: str
    iterations: int = Field(default=5, ge=3, le=10)


@router.post("/run")
def run_benchmark(request: BenchmarkRequest):

    department = request.department.strip()

    if department not in ALLOWED_DEPARTMENTS:
        raise HTTPException(
            status_code=400,
            detail="Invalid department."
        )

    connection = None
    cursor = None

    query = """
        SELECT *
        FROM employees
        WHERE department = %s
    """

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Inspect the optimizer's chosen access method
        cursor.execute(
            """
            EXPLAIN
            SELECT *
            FROM employees
            WHERE department = %s
            """,
            (department,)
        )

        plan = cursor.fetchone()

        # Warm-up execution (not included in measurements)
        cursor.execute(query, (department,))
        cursor.fetchall()

        execution_times = []
        rows_returned = 0

        # Repeated benchmark measurements
        for _ in range(request.iterations):

            start = time.perf_counter()

            cursor.execute(query, (department,))
            results = cursor.fetchall()

            end = time.perf_counter()

            execution_times.append(
                round((end - start) * 1000, 3)
            )

            rows_returned = len(results)

        return {
            "status": "success",
            "department": department,
            "iterations": request.iterations,
            "index_used": plan["key"] == "idx_department",
            "index_name": plan["key"],
            "access_method": plan["type"],
            "estimated_rows": plan["rows"],
            "rows_returned": rows_returned,
            "execution_times_ms": execution_times,
            "median_execution_time_ms": round(
                statistics.median(execution_times), 3
            ),
            "average_execution_time_ms": round(
                statistics.mean(execution_times), 3
            ),
            "minimum_execution_time_ms": min(execution_times),
            "maximum_execution_time_ms": max(execution_times)
        }

    except mysql.connector.Error:
        raise HTTPException(
            status_code=500,
            detail="Database benchmark failed."
        )

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

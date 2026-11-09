import statistics
import threading
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from mysql.connector import Error

from backend.app.database import (
    get_connection,
    get_index_connection
)

router = APIRouter()
comparison_lock = threading.Lock()

INDEX_NAME = "idx_department"
TABLE_NAME = "employees"

ALLOWED_DEPARTMENTS = {
    "Engineering", "Marketing", "HR", "Finance",
    "Sales", "Operations", "IT", "Research"
}


class ComparisonRequest(BaseModel):
    department: str
    iterations: int = Field(default=10, ge=5, le=30)


def check_index(cursor):
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s
    """, (TABLE_NAME, INDEX_NAME))

    return cursor.fetchone()["total"] > 0


def set_index(should_exist):
    connection = get_index_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        exists = check_index(cursor)

        if should_exist and not exists:
            cursor.execute(
                "CREATE INDEX idx_department "
                "ON employees(department)"
            )

        elif not should_exist and exists:
            cursor.execute(
                "DROP INDEX idx_department ON employees"
            )

    finally:
        cursor.close()
        connection.close()


def run_measurement(department, iterations):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM employees
        WHERE department = %s
    """

    try:
        cursor.execute(
            "EXPLAIN SELECT * FROM employees "
            "WHERE department = %s",
            (department,)
        )

        plan = cursor.fetchone()

        # Warm-up execution
        cursor.execute(query, (department,))
        cursor.fetchall()

        times = []
        rows_returned = 0

        for _ in range(iterations):
            start = time.perf_counter()

            cursor.execute(query, (department,))
            results = cursor.fetchall()

            end = time.perf_counter()

            times.append(round((end - start) * 1000, 3))
            rows_returned = len(results)

        return {
            "index_used": plan["key"] == INDEX_NAME,
            "index_name": plan["key"],
            "access_method": plan["type"],
            "estimated_rows": plan["rows"],
            "rows_returned": rows_returned,
            "execution_times_ms": times,
            "median_execution_time_ms": round(
                statistics.median(times), 3
            ),
            "average_execution_time_ms": round(
                statistics.mean(times), 3
            ),
            "standard_deviation_ms": round(
                statistics.stdev(times), 3
            ) if len(times) > 1 else 0
        }

    finally:
        cursor.close()
        connection.close()


@router.post("/compare")
def compare_performance(request: ComparisonRequest):

    department = request.department.strip()

    if department not in ALLOWED_DEPARTMENTS:
        raise HTTPException(
            status_code=400,
            detail="Invalid department."
        )

    if not comparison_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409,
            detail="Another comparison is already running."
        )

    original_index_state = None
    without_index_times = []
    with_index_times = []
    without_index = None
    with_index = None
    operation_error = None
    restoration_error = None

    try:
        connection = get_index_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            original_index_state = check_index(cursor)
        finally:
            cursor.close()
            connection.close()

        # Warm up both configurations before measurement
        set_index(False)
        run_measurement(department, 1)

        set_index(True)
        run_measurement(department, 1)

        # Alternate configurations to reduce order bias
        for run_number in range(request.iterations):

            if run_number % 2 == 0:
                set_index(False)
                result = run_measurement(department, 1)
                without_index_times.extend(
                    result["execution_times_ms"]
                )

                set_index(True)
                result = run_measurement(department, 1)
                with_index_times.extend(
                    result["execution_times_ms"]
                )

            else:
                set_index(True)
                result = run_measurement(department, 1)
                with_index_times.extend(
                    result["execution_times_ms"]
                )

                set_index(False)
                result = run_measurement(department, 1)
                without_index_times.extend(
                    result["execution_times_ms"]
                )

        # Capture the final execution plans
        set_index(False)
        without_index = run_measurement(department, 1)

        set_index(True)
        with_index = run_measurement(department, 1)

        if (
            without_index["rows_returned"]
            != with_index["rows_returned"]
        ):
            raise RuntimeError("Row counts do not match.")

        without_median = statistics.median(
            without_index_times
        )

        with_median = statistics.median(
            with_index_times
        )

    except Exception as error:
        operation_error = error

    finally:
        try:
            if original_index_state is not None:
                set_index(original_index_state)
        except Exception as error:
            restoration_error = error

        comparison_lock.release()

    if restoration_error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Index restoration failed. "
                "Verify SHOW INDEX FROM employees."
            )
        )

    if operation_error:
        raise HTTPException(
            status_code=500,
            detail="Performance comparison failed."
        )

    improvement = (
        ((without_median - with_median) / without_median) * 100
        if without_median > 0 else None
    )

    return {
        "status": "success",
        "department": department,
        "iterations_per_condition": request.iterations,
        "without_index": {
            "index_used": False,
            "access_method": without_index["access_method"],
            "estimated_rows": without_index["estimated_rows"],
            "rows_returned": without_index["rows_returned"],
            "execution_times_ms": without_index_times,
            "median_execution_time_ms": round(
                without_median, 3
            ),
            "average_execution_time_ms": round(
                statistics.mean(without_index_times), 3
            ),
            "standard_deviation_ms": round(
                statistics.stdev(without_index_times), 3
            )
        },
        "with_index": {
            "index_used": True,
            "index_name": INDEX_NAME,
            "access_method": with_index["access_method"],
            "estimated_rows": with_index["estimated_rows"],
            "rows_returned": with_index["rows_returned"],
            "execution_times_ms": with_index_times,
            "median_execution_time_ms": round(
                with_median, 3
            ),
            "average_execution_time_ms": round(
                statistics.mean(with_index_times), 3
            ),
            "standard_deviation_ms": round(
                statistics.stdev(with_index_times), 3
            )
        },
        "improvement_percent": round(improvement, 2)
        if improvement is not None else None
    }

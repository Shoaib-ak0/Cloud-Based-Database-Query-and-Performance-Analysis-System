import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.app.database import get_connection

router = APIRouter()


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)


@router.post("/execute")
def execute_query(request: QueryRequest):

    sql = request.query.strip()

    # Basic SELECT-only validation
    if not sql.upper().startswith("SELECT "):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries are allowed."
        )

    # Reject multiple SQL statements
    if ";" in sql.rstrip(";"):
        raise HTTPException(
            status_code=400,
            detail="Multiple SQL statements are not allowed."
        )

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        start_time = time.perf_counter()

        cursor.execute(sql)

        results = cursor.fetchmany(100)

        execution_time = (
            time.perf_counter() - start_time
        ) * 1000

        return {
            "status": "success",
            "query": sql,
            "execution_time_ms": round(execution_time, 3),
            "rows_returned": len(results),
            "results": results
        }

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Query execution failed."
        )

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

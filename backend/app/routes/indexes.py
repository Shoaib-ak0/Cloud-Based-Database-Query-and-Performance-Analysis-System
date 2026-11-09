from fastapi import APIRouter, HTTPException
from mysql.connector import Error

from backend.app.database import get_index_connection

router = APIRouter()

INDEX_NAME = "idx_department"
TABLE_NAME = "employees"
COLUMN_NAME = "department"


def index_exists(cursor):
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = %s
          AND index_name = %s
    """, (TABLE_NAME, INDEX_NAME))

    return cursor.fetchone()["total"] > 0


@router.post("/create")
def create_index():

    connection = None
    cursor = None

    try:
        connection = get_index_connection()
        cursor = connection.cursor(dictionary=True)

        if index_exists(cursor):
            return {
                "status": "success",
                "message": "Index already exists",
                "index_name": INDEX_NAME
            }

        cursor.execute(
            "CREATE INDEX idx_department "
            "ON employees(department)"
        )

        return {
            "status": "success",
            "message": "Index created successfully",
            "index_name": INDEX_NAME
        }

    except Error:
        raise HTTPException(
            status_code=500,
            detail="Index creation failed"
        )

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


@router.delete("/delete")
def delete_index():

    connection = None
    cursor = None

    try:
        connection = get_index_connection()
        cursor = connection.cursor(dictionary=True)

        if not index_exists(cursor):
            return {
                "status": "success",
                "message": "Index does not exist",
                "index_name": INDEX_NAME
            }

        cursor.execute(
            "DROP INDEX idx_department ON employees"
        )

        return {
            "status": "success",
            "message": "Index deleted successfully",
            "index_name": INDEX_NAME
        }

    except Error:
        raise HTTPException(
            status_code=500,
            detail="Index deletion failed"
        )

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

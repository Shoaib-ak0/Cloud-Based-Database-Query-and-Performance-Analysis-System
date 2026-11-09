from fastapi import APIRouter, HTTPException
from backend.app.database import get_connection

router = APIRouter()


@router.get("/stats")
def get_database_stats():

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Total employee records
        cursor.execute(
            "SELECT COUNT(*) AS total_employees FROM employees"
        )
        total = cursor.fetchone()

        # Department distribution
        cursor.execute("""
            SELECT department, COUNT(*) AS total
            FROM employees
            GROUP BY department
            ORDER BY total DESC
        """)
        departments = cursor.fetchall()

        # Salary statistics
        cursor.execute("""
            SELECT
                MIN(salary) AS minimum_salary,
                MAX(salary) AS maximum_salary,
                ROUND(AVG(salary), 2) AS average_salary
            FROM employees
        """)
        salary = cursor.fetchone()

        return {
            "total_employees": total["total_employees"],
            "total_departments": len(departments),
            "department_distribution": departments,
            "salary_statistics": salary
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve database statistics"
        )

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

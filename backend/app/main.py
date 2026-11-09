from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from backend.app.database import get_connection
from backend.app.routes.stats import router as stats_router
from backend.app.routes.query import router as query_router
from backend.app.routes.benchmark import router as benchmark_router
from backend.app.routes.indexes import router as indexes_router
from backend.app.routes.comparison import router as comparison_router

app = FastAPI(
    title="Database Performance Analysis API",
    description="API for database query and performance analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"]
)

app.include_router(
	stats_router,
	prefix="/api/database",
	tags=["Database Statistics"]
)


app.include_router(
	query_router,
	prefix="/api/query",
	tags=["Query Execution"]
)

app.include_router(
	benchmark_router,
	prefix="/api/benchmark",
	tags=["Benchmark"]
)

app.include_router(
	indexes_router,
	prefix="/api/index",
	tags=["Index Management"]
)
app.include_router(
	comparison_router,
	prefix="/api/benchmark",
	tags=["Benchmark Comparsion"]
)

@app.get("/")
def home():
    return {
        "message": "Database Performance API is running"
    }


@app.get("/api/health")
def health_check():

    connection = None

    try:
        connection = get_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")

        version = cursor.fetchone()[0]

        cursor.close()

        return {
            "status": "healthy",
            "database": "connected",
            "mysql_version": version
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )

    finally:
        if connection and connection.is_connected():
            connection.close()

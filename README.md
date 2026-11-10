# Database Performance Lab

A cloud-based database query and performance analysis system built with **Python, FastAPI, MySQL, HTML, CSS and JavaScript**. The application allows users to execute SQL queries, manage database indexes, benchmark query execution and compare indexed versus non-indexed performance through an interactive dashboard.

## Project Overview

Database Performance Lab demonstrates how database indexing affects query execution performance using a MySQL database containing 100,000 synthetic employee records.

The application provides a web interface for executing SELECT queries, viewing database statistics, managing indexes and comparing query execution times.

The project is deployed on an Ubuntu virtual machine hosted on AWS EC2.

## Features

- Interactive database performance dashboard.
- Execution of SELECT queries through a web interface.
- Query execution time measurement.
- Database statistics and department distribution.
- Performance benchmarking with configurable iterations.
- Indexed versus non-indexed query comparison.
- Dynamic creation and deletion of the department index.
- Query execution plan inspection using MySQL EXPLAIN.
- Performance visualization using Chart.js.
- AWS EC2 deployment with Nginx and FastAPI.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js |
| Backend | Python, FastAPI |
| Database | MySQL |
| Database Connector | MySQL Connector/Python |
| Configuration | Python-dotenv |
| ASGI Server | Uvicorn |
| Web Server | Nginx |
| Cloud Platform | AWS EC2 |
| Operating System | Ubuntu 24.04 |

## System Architecture

```text
             User / Browser
                    |
                    v
             Nginx Web Server
                    |
          +---------+---------+
          |                   |
          v                   v
     Frontend Files       FastAPI Backend
     HTML/CSS/JS          Python
                              |
                              v
                         MySQL Database
                              |
                       employees table
                        100,000 records
                              |
                    +---------+---------+
                    |                   |
                    v                   v
              Indexed Query       Full Table Scan
                    |                   |
                    +---------+---------+
                              |
                              v
                    Performance Analysis
                              |
                              v
                     Dashboard / Charts
```

## Database Design

**Database:** `performance_lab`

**Table:** `employees`

| Column | Data Type | Description |
|---|---|---|
| id | INT | Primary key |
| name | VARCHAR(100) | Employee name |
| department | VARCHAR(100) | Employee department |
| salary | DECIMAL(10,2) | Employee salary |
| city | VARCHAR(100) | Employee city |

**Dataset details:**
- Total records: 100,000
- Total departments: 8
- Primary key: `id`
- Secondary index: `idx_department`

The department index is created using:

```sql
CREATE INDEX idx_department
ON employees(department);
```

## Performance Analysis

The system compares query execution under two conditions:

1. Without index: MySQL performs a full table scan.
2. With index: MySQL can use the `idx_department` index.

The comparison endpoint:
- Checks the original index state.
- Performs warm-up executions.
- Alternates indexed and non-indexed measurements.
- Collects execution times using Python's `time.perf_counter()`.
- Calculates median, average and standard deviation.
- Calculates percentage improvement using median execution times.
- Restores the original index state.

Percentage improvement:

```text
Improvement (%) =
((Time Without Index - Time With Index)
 / Time Without Index) * 100
```

Actual performance depends on query conditions, database caching, dataset characteristics and server resources.

## API Documentation

Base path: `/api`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Database health check |
| GET | `/database/stats` | Database statistics |
| POST | `/query/execute` | Execute SELECT query |
| POST | `/benchmark/run` | Benchmark current index configuration |
| POST | `/benchmark/compare` | Compare indexed and non-indexed performance |
| POST | `/index/create` | Create department index |
| DELETE | `/index/delete` | Delete department index |

### Example API Requests

**Execute a query**

`POST /api/query/execute`

```json
{
  "query": "SELECT * FROM employees LIMIT 10"
}
```

**Run a benchmark**

`POST /api/benchmark/run`

```json
{
  "department": "Engineering",
  "iterations": 5
}
```

**Compare indexed and non-indexed performance**

`POST /api/benchmark/compare`

```json
{
  "department": "Engineering",
  "iterations": 10
}
```

The query endpoint accepts SELECT statements only and returns up to 100 rows.

## Installation and Local Setup

### Prerequisites

- Python 3.10 or later
- MySQL Server 8.0 or later
- Git
- A modern web browser

### 1. Clone the repository

```bash
git clone https://github.com/Shoaib-ak0/Cloud-Based-Database-Query-and-Performance-Analysis-System.git

cd Cloud-Based-Database-Query-and-Performance-Analysis-System
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / Ubuntu**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=app_user
DB_PASSWORD=your_password
DB_NAME=performance_lab

INDEX_DB_HOST=localhost
INDEX_DB_PORT=3306
INDEX_DB_USER=app_user
INDEX_DB_PASSWORD=your_password
INDEX_DB_NAME=performance_lab
CORS_ORIGINS=http://127.0.0.1:5500,http://localhost:5500
```
For production deployment behind Nginx, leave CORS_ORIGINS empty because the frontend and API share the same origin.
Never commit your `.env` file or .

Never commit your `.env` file or database credentials to GitHub.

### 5. Create the database

```sql
CREATE DATABASE performance_lab;
```

Create the `employees` table:

```sql
USE performance_lab;

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    city VARCHAR(100) NOT NULL
);
```

### 6. Generate sample records

```bash
python generate_date.py
```

The script generates 100,000 synthetic employee records.

### 7. Start the backend

```bash
uvicorn backend.app.main:app --reload
```

Backend address:

`http://127.0.0.1:8000`

API health endpoint:

`http://127.0.0.1:8000/api/health`

### 8. Open the frontend

Open `frontend/index.html` using a local development server, such as VS Code Live Server.

For local development, configure the frontend API base URL in `frontend/js/api.js` to point to the local FastAPI server:

```javascript
const API_BASE_URL = "http://127.0.0.1:8000/api";
```

For the EC2 deployment, use:

```javascript
const API_BASE_URL = "/api";
```

## AWS EC2 Deployment

The application is deployed on an Ubuntu 24.04 EC2 instance.

Deployment components:

- AWS EC2 for cloud hosting.
- MySQL Server for database storage.
- FastAPI with Uvicorn for backend execution.
- Nginx for frontend hosting and API reverse proxy.
- systemd for automatic backend service management.

The production frontend uses the same-origin `/api` path, with Nginx forwarding API requests to Uvicorn on `127.0.0.1:8000`.

The application is accessed through the EC2 public IPv4 address over HTTP.

**Note:** The public IP may change if the instance is stopped and restarted.

## Repository Structure

```text
database-performance-lab/
│
├── backend/
│   └── app/
│       ├── routes/
│       │   ├── benchmark.py
│       │   ├── comparison.py
│       │   ├── indexes.py
│       │   ├── query.py
│       │   └── stats.py
│       │
│       ├── services/
│       ├── database.py
│       └── main.py
│
├── frontend/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   ├── api.js
│   │   ├── app.js
│   │   ├── charts.js
│   │   └── dashboard.js
│   │
│   └── index.html
│
├── generate_date.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Future Enhancements

- Support for additional SQL query types with appropriate access controls.
- Comparison of multiple indexing strategies.
- Query execution plan visualization.
- Support for larger datasets.
- Historical benchmark storage and analysis.
- Authentication and role-based access control.
- HTTPS configuration.

## Project Objective

The objective is to demonstrate the practical impact of database indexing on query execution performance through a cloud-hosted, interactive web application.

## Author

**Shoaib Akhtar**

GitHub: [Shoaib-ak0](https://github.com/Shoaib-ak0)

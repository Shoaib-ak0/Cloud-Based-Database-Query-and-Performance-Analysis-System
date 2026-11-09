import mysql.connector
import random
import time
from getpass import getpass

# ----------------------------------
# 1. Database configuration
# ----------------------------------

DB_CONFIG = {
    "host": "localhost",
    "user": "lab_user",
    "password": getpass("Enter MySQL password: "),
    "database": "performance_lab"
}

# ----------------------------------
# 2. Synthetic employee data
# ----------------------------------

first_names = [
    "Rahul", "Amit", "Shoaib", "Priya", "Ankit",
    "Neha", "Arjun", "Riya", "Vikram", "Sneha",
    "Karan", "Ayesha", "Rohan", "Ishita", "Aditya"
]

last_names = [
    "Sharma", "Khan", "Das", "Roy", "Verma",
    "Gupta", "Singh", "Patel", "Kumar", "Malik"
]

departments = [
    "Engineering",
    "Marketing",
    "HR",
    "Finance",
    "Sales",
    "Operations",
    "IT",
    "Research"
]

cities = [
    "Kolkata",
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Chennai",
    "Hyderabad",
    "Pune",
    "Jaipur"
]

def generate_employee():

    name = (
        random.choice(first_names)
        + " "
        + random.choice(last_names)
    )

    department = random.choice(departments)

    salary = round(random.uniform(25000, 150000), 2)

    city = random.choice(cities)

    return (name, department, salary, city)


# ----------------------------------
# 3. Generate and insert records
# ----------------------------------

TOTAL_RECORDS = 100_000
BATCH_SIZE = 1000

connection = None
cursor = None

try:
    start_time = time.perf_counter()

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    print("Connected to MySQL successfully!")

    insert_query = """
        INSERT INTO employees
        (name, department, salary, city)
        VALUES (%s, %s, %s, %s)
    """

    for start in range(0, TOTAL_RECORDS, BATCH_SIZE):

        batch = [
            generate_employee()
            for _ in range(
                min(BATCH_SIZE, TOTAL_RECORDS - start)
            )
        ]

        cursor.executemany(insert_query, batch)
        connection.commit()

        inserted = start + len(batch)

        print(
            f"Inserted {inserted:,}/{TOTAL_RECORDS:,} records"
        )

    end_time = time.perf_counter()

    print("\nData generation completed!")
    print(f"Total time: {end_time - start_time:.2f} seconds")

    cursor.execute("SELECT COUNT(*) FROM employees")

    total = cursor.fetchone()[0]
    print(f"Total employees in database: {total:,}")

except mysql.connector.Error as error:
    if connection and connection.is_connected():
        connection.rollback()

    print("MySQL error:", error)

finally:
    if cursor:
        cursor.close()

    if connection and connection.is_connected():
        connection.close()

    print("Database connection closed.")


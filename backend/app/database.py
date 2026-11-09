import os 
import mysql.connector

from dotenv import load_dotenv

# Load environment variable from project root
load_dotenv()

DB_CONFIG = {
	"host": os.getenv("DB_HOST"),
	"port": int(os.getenv("DB_PORT",3306)),
	"user": os.getenv("DB_USER"),
	"password": os.getenv("DB_PASSWORD"),
	"database": os.getenv("DB_NAME")
}


def get_connection():
	
	connection = mysql.connector.connect(
	**DB_CONFIG,
	connection_timeout=5
	)

	return connection

def get_index_connection():

    config = {
        "host": os.getenv("INDEX_DB_HOST"),
        "port": int(os.getenv("INDEX_DB_PORT", 3306)),
        "user": os.getenv("INDEX_DB_USER"),
        "password": os.getenv("INDEX_DB_PASSWORD"),
        "database": os.getenv("INDEX_DB_NAME"),
        "connection_timeout": 5
    }

    return mysql.connector.connect(**config)

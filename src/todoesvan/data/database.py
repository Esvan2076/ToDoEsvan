import os

import psycopg2
from dotenv import load_dotenv

from todoesvan.utils.logging import get_logger

load_dotenv()

logger = get_logger(__name__)

# Load environment variables
load_dotenv()

def get_db_connection():
    """Establishes connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except Exception:
        logger.exception("Failed to connect to database")
        return None

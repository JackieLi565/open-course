from database import init_database
from psycopg2 import DatabaseError

try:
    init_database()
except (Exception, DatabaseError) as error:
    exit(f"Error: {error}")

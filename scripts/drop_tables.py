from database import drop_tables
from psycopg2 import DatabaseError

try:
  drop_tables()
except (Exception, DatabaseError) as error:
    exit(f"Error: {error}")
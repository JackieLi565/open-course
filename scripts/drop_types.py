from database import drop_types
from psycopg2 import DatabaseError

try:
  drop_types()
except (Exception, DatabaseError) as error:
    exit(f"Error: {error}")
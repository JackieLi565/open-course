"""
courses
  - course
"""
from psycopg2 import DatabaseError
from database import database_connection, get_all_category_uri
from utils import build_url
import requests

static = '/jcr:content/content/rescalendarcoursestack.data.1.json'

def get_course_data(url: str):
    """
        important data signature
        {
            data: {
                page: str
                courseCode: str
                longTitle: str

                lectureLength?: str
                labLength?: str
                
                gpaWeight: str
                courseCount: str
                courseDescription: str
                
                courseAttribute?: "LL"

                antirequisites?: str |
                prerequisites?: str  | <- JSON-escaped HTML
                corequisites?: str   |
            }[]
        }
    """

conn, curr = None, None
try:
    conn = database_connection()
    curr = conn.cursor()

    curr.execute(get_all_category_uri())

    rows = curr.fetchall()
    
    for row in rows:
        url = build_url(row[0][:-5] + static)
        res = requests.get(url)

        if res.status_code != 200:
            print(f"Warning: request to {url} failed")
        
        print(res.json())
        

except (Exception, DatabaseError) as error:
    exit(f"Error: {error}")
finally:
    if conn and curr:
        conn.close()
        curr.close()


"""
Meta
    - prefix
    - category
    - faculty
"""
from utils import get_argv, build_url, get_html
from database import get_faculty_id, insert_program, database_connection
from psycopg2 import DatabaseError
import uuid

args = get_argv()

if len(args) > 1:
    print(f'Error: too many arguments provided')
    exit()

url_path = '/calendar/2023-2024/programs/'

if len(args) == 1:
    url_path = args[0]

soup = get_html(build_url(url_path))

table_rows = soup.findAll('tr')[1::] # exclude header

program_map = {}

for row in table_rows:
    tds = row.find_all('td')
    a_tag = tds[1].find('a')

    faculty = tds[0].text.strip()
    program = a_tag.text.strip()
    href = a_tag.get('href').strip()

    program_map[program] = {
        'href': href,
        'faculty': faculty
    }

conn, curr = None, None
try:
    conn = database_connection()
    curr = conn.cursor()

    for program_name, data in program_map.items():
        curr.execute(get_faculty_id(data['faculty']))
        row = curr.fetchone()

        if not row:
            print(f"Warning: missing faculty {data['faculty']} for {program_name}")
            continue
        
        query = insert_program(uuid.uuid4(), program_name, data['href'], row[0])
        curr.execute(query)
    
    conn.commit()
except (Exception, DatabaseError) as error:
    exit(f"Error: {error}")
finally:
    if conn and curr:
        conn.close()
        curr.close()

    
"""
1
"""

from utils import get_argv, build_url, get_html
from psycopg2 import DatabaseError
from database import (
    database_connection,
    insert_faculty,
    insert_category,
    insert_category_faculty,
    insert_prefix,
)
from uuid import uuid4
import re

args = get_argv()

if len(args) > 1:
    print(f"Error: too many arguments provided")
    exit()


def parse_course_info(course_string):
    parts = course_string.split(" (", 1)
    if len(parts) != 2:
        return None

    course_name = parts[0].strip()
    courses = parts[1].strip()

    if courses.endswith(")"):
        courses = courses[:-1]
    else:
        return None

    course_list = [course.strip() for course in courses.split(",")]

    return {"name": course_name, "prefixes": course_list}


url_path = "/calendar/2023-2024/courses/"

if len(args) == 1:
    url_path = args[0]

soup = get_html(build_url(url_path))

table_rows = soup.findAll("tr")[1::]  # exclude header

faculty_map = {}
category_map = {}

entries = []

for row in table_rows:
    tds = row.find_all("td")
    a_tag = tds[0].find("a")

    course = parse_course_info(a_tag.text)

    if not course:
        print(f"Error: {a_tag.text}")
        continue

    faculties = [
        faculty.strip()
        for faculty in tds[1].text.replace("\u00a0", " ").strip().split(" / ")
    ]
    href = a_tag.get("href").strip()
    prefixes = course["prefixes"]
    category = course["name"]

    for faculty in faculties:
        if faculty not in faculty_map:
            faculty_map[faculty] = str(uuid4())

    category_map[category] = str(uuid4())

    entries.append(
        {
            "faculties": faculties,
            "href": re.sub(r"\.html.*", "", href),
            "prefixes": prefixes,
            "category": category,
        }
    )

conn, curr = None, None

try:
    conn = database_connection()
    curr = conn.cursor()

    # insert all faculty data
    for faculty, faculty_id in faculty_map.items():
        curr.execute(insert_faculty(), (faculty_id, faculty))

    # insert all category, prefix & category_faculty relationships
    for entry in entries:
        category, href = entry["category"], entry["href"]
        category_id = category_map[category]

        curr.execute(insert_category(), (category_id, category, href))

        for faculty in entry["faculties"]:
            faculty_id = faculty_map[faculty]
            curr.execute(
                insert_category_faculty(), (str(uuid4()), category_id, faculty_id)
            )

        for prefix in entry["prefixes"]:
            curr.execute(insert_prefix(), (str(uuid4()), prefix, category_id))

    conn.commit()

except (Exception, DatabaseError) as error:
    exit(f"Error: {error}")
finally:
    if conn and curr:
        conn.close()
        curr.close()

"""
3
"""

from uuid import uuid4
import warnings
import requests
from psycopg2 import DatabaseError
from database import (
    database_connection,
    get_all_category_uri,
    insert_prerequisite,
    insert_antirequisite,
    insert_corequisite,
    get_antirequisite_id,
    get_corequisite_id,
    get_prefix_id,
    insert_course,
    get_course_id,
    get_prerequisite_id,
    insert_course_prerequisite,
    insert_course_antirequisite,
    insert_course_corequisite,
)
from utils import build_url
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning


def get_json_payload(uri: str) -> dict:
    data_endpoint = "/jcr:content/content/rescalendarcoursestack.data.1.json"
    url = build_url(uri + data_endpoint)
    res = requests.get(url)

    if res.status_code != 200:
        print(f"Warning: failed response from {url}")
        return None

    return res.json()


def get_course_data(courses: list[dict]) -> list[dict]:
    result = []
    for course in courses:
        prefix, code = course["courseCode"].split(" ")
        liberal = course.get("courseAttribute")

        if liberal:
            is_lower = "LL" in liberal
            is_upper = "UL" in liberal
            if is_lower and is_upper:
                liberal = "LL/UL"
            elif is_lower:
                liberal = "LL"
            elif is_upper:
                liberal = "UL"

        contract = ""

        lecture = course.get("lectureLength")
        if lecture:
            contract += f"lecture {lecture}"
        lab = course.get("labLength")
        if lab:
            contract += f"lab {lab}"
        tutorial = course.get("tutorialLength")
        if tutorial:
            contract += f"tutorial {tutorial}"

        if contract == "":
            raise Exception("contract is empty")

        result.append(
            {
                "uri": course["page"],
                "title": course["longTitle"],
                "description": course["courseDescription"],
                "contract": contract[:-1],  # remove the trailing .
                "weight": course["gpaWeight"],
                "code": code,
                "prefix": prefix,
                "liberal": liberal,
                "units": course.get("billingUnit"),
                "count": course.get("courseCount"),
            }
        )

    return result


def get_requisite_data(courses: list[dict]) -> list[dict]:
    entries = {"pre": "prerequisites", "anti": "antirequisites", "co": "corequisites"}

    def helper(json_escaped_html: str):
        requisite = json_escaped_html.encode("latin1").decode("unicode-escape")
        soup = BeautifulSoup(requisite, "html.parser")
        result = []
        for link in soup.find_all("a"):
            href = link["href"]
            if ".html" in href:
                href = href[:-5]

            result.append(href)

        return result

    result = []
    for course in courses:
        data = {"uri": course["page"]}

        for key, requisite in entries.items():
            json_escaped_html = course.get(requisite)
            if not json_escaped_html:
                continue

            data[key] = helper(json_escaped_html)

        result.append(data)

    return result


warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module="bs4")
conn, curr = None, None
try:
    conn = database_connection()
    curr = conn.cursor()

    curr.execute(get_all_category_uri())

    rows = curr.fetchall()

    check = 0

    for row in rows:
        print(f"\nStarting - {row}\n")

        uri = row[0]

        payload = get_json_payload(uri)
        courses = payload.get("data")

        if not courses:
            print(f"\n\Waring - {uri}, contains no courses\n")
            continue

        for course in get_course_data(courses):
            curr.execute(get_prefix_id(), (course["prefix"],))
            prefix = curr.fetchone()

            if not prefix:
                print(f"Warning - prefix '{course['prefix']}' for {uri} not found")
                continue

            data = (
                str(uuid4()),
                course["title"],
                course["description"],
                course["code"],
                course["uri"],
                course["liberal"],
                course["contract"],
                course["weight"],
                course["units"],
                course["count"],
                prefix[0],
            )

            curr.execute(insert_course(), data)
            print(f"Mutation Complete - {course['title']}")

    for row in rows:
        print("\n Starting Requisites \n")
        uri = row[0]

        payload = get_json_payload(uri)
        courses = payload.get("data")
        requisites = get_requisite_data(courses)

        for requisite in requisites:
            uri = requisite["uri"]

            def helper(
                uris: list[str] | None, get_requisite_id, insert_requisite, bridge_table
            ):
                if not uris:
                    return

                for uri in uris:
                    curr.execute(get_course_id(), (uri,))
                    course_id = curr.fetchone()

                    if not course_id:
                        print(f"Warning - {uri} DNE")
                        continue

                    curr.execute(get_requisite_id(), (course_id,))
                    requisite_id = curr.fetchone()

                    if not requisite_id:
                        requisite_id = str(uuid4())
                        curr.execute(insert_requisite(), (requisite_id, course_id))
                    else:
                        requisite_id = requisite_id[0]

                    curr.execute(
                        bridge_table(), (str(uuid4()), course_id, requisite_id)
                    )

            helper(
                requisite.get("pre"),
                get_prerequisite_id,
                insert_prerequisite,
                insert_course_prerequisite,
            )
            helper(
                requisite.get("anti"),
                get_antirequisite_id,
                insert_antirequisite,
                insert_course_antirequisite,
            )
            helper(
                requisite.get("co"),
                get_corequisite_id,
                insert_corequisite,
                insert_course_corequisite,
            )

    conn.commit()
except (Exception, DatabaseError) as error:
    exit(f"Error: {error}")
finally:
    if conn and curr:
        conn.close()
        curr.close()

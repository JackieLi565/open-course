import json
import os
import psycopg2
from psycopg2.extensions import connection

script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, "database.config.json")


def database_connection() -> connection:
    with open(config_file_path, "r") as file:
        config = json.load(file)

    connection = psycopg2.connect(
        host=config["host"],
        database=config["database"],
        user=config["user"],
        password=config["password"],
    )

    return connection


def init_database():
    types = {"liberal": "CREATE TYPE liberal AS ENUM ('LL', 'UL', 'LL/UL');"}

    schema = {
        "faculty": """
        CREATE TABLE faculty (
            id VARCHAR(36) PRIMARY KEY, 
            name TEXT UNIQUE NOT NULL
        );
        """,
        "category": """
        CREATE TABLE category (
            id VARCHAR(36) PRIMARY KEY, 
            name TEXT NOT NULL, 
            uri TEXT NOT NULL
        );
        """,
        "category_faculty": """
        CREATE TABLE category_faculty (
            id VARCHAR(36) PRIMARY KEY, 
            fk_category VARCHAR(36) REFERENCES category(id), 
            fk_faculty VARCHAR(36) REFERENCES faculty(id)
        ); 
        """,
        "prefix": """
        CREATE TABLE prefix (
            id VARCHAR(36) PRIMARY KEY, 
            name VARCHAR(4) UNIQUE NOT NULL, 
            fk_category VARCHAR(36) REFERENCES category(id)
        );
        """,
        "program": """
        CREATE TABLE program (
            id VARCHAR(36) PRIMARY KEY, 
            name TEXT NOT NULL, 
            uri TEXT NOT NULL, 
            fk_faculty VARCHAR(36) REFERENCES faculty(id)
        );
        """,
        "course": """
        CREATE TABLE course (
            id VARCHAR(36) PRIMARY KEY, 
            title TEXT NOT NULL, 
            description TEXT, 
            code TEXT NOT NULL, 
            uri TEXT NOT NULL, 
            contract TEXT NOT NULL, 
            weight REAL NOT NULL, 
            billing_units VARCHAR(16), 
            lib LIBERAL,
            count REAL, 
            fk_prefix VARCHAR(36) REFERENCES prefix(id)
        );
        """,
        "program_course": """
        CREATE TABLE program_course (
            id VARCHAR(36) PRIMARY KEY, 
            fk_program VARCHAR(36) REFERENCES program(id), 
            fk_course VARCHAR(36) REFERENCES course(id), 
            semester BIGINT
        );
        """,
        "prerequisite": """
        CREATE TABLE prerequisite (
            id VARCHAR(36) PRIMARY KEY, 
            fk_course VARCHAR(36) REFERENCES course(id)
        );
        """,
        "antirequisite": """
        CREATE TABLE antirequisite (
            id VARCHAR(36) PRIMARY KEY, 
            fk_course VARCHAR(36) REFERENCES course(id)
        );
        """,
        "corequisite": """
        CREATE TABLE corequisite (
            id VARCHAR(36) PRIMARY KEY, 
            fk_course VARCHAR(36) REFERENCES course(id)
        );
        """,
        "course_prerequisite": """
        CREATE TABLE course_prerequisite (
            id VARCHAR(36) PRIMARY KEY, 
            fk_course VARCHAR(36) REFERENCES course(id), 
            fk_prerequisite VARCHAR(36) REFERENCES prerequisite(id)
        );
        """,
        "course_antirequisite": """
        CREATE TABLE course_antirequisite (
            id VARCHAR(36) PRIMARY KEY, 
            fk_course VARCHAR(36) REFERENCES course(id), 
            fk_antirequisite VARCHAR(36) REFERENCES antirequisite(id)
        );
        """,
        "course_corequisite": """
        CREATE TABLE course_corequisite (
            id VARCHAR(36) PRIMARY KEY, 
            fk_course VARCHAR(36) REFERENCES course(id), 
            fk_corequisite VARCHAR(36) REFERENCES corequisite(id)
        );
        """,
    }

    conn = database_connection()
    curr = conn.cursor()

    for type_, data in types.items():
        curr.execute(data)
        print(f"Created type: {type_}")

    print()

    for table, data in schema.items():
        curr.execute(data)
        print(f"Created table: {table}")

    conn.commit()
    conn.close()
    curr.close()


def drop_types():
    types = ["drop type liberal"]

    conn = database_connection()
    curr = conn.cursor()

    for command in types:
        curr.execute(command)

    conn.commit()
    conn.close()
    curr.close()


def drop_tables():
    sql = [
        "drop table category_faculty;",
        "drop table program_course;",
        "drop table program;",
        "drop table course_prerequisite;",
        "drop table course_antirequisite;",
        "drop table course_corequisite;",
        "drop table corequisite;",
        "drop table prerequisite;",
        "drop table antirequisite;",
        "drop table course;",
        "drop table prefix;",
        "drop table category;",
        "drop table faculty",
    ]

    conn = database_connection()
    curr = conn.cursor()

    for command in sql:
        curr.execute(command)

    conn.commit()
    conn.close()
    curr.close()


def insert_faculty():
    return """
    insert into faculty (id, name)
    values (%s, %s);
    """


def insert_category():
    return """
    insert into category (id, name, uri) 
    values (%s, %s, %s);
    """


def insert_category_faculty():
    return """
    insert into category_faculty (id, fk_category, fk_faculty)
    values (%s, %s, %s); 
    """


def insert_prefix():
    return """
    insert into prefix (id, name, fk_category) 
    values (%s, %s, %s);
    """


def insert_program():
    return """
    insert into program (id, name, uri, fk_faculty)
    values (%s, %s, %s, %s);
    """


def insert_course():
    return """
    insert into course (id, title, description, code, uri, lib, contract, weight, billing_units, count, fk_prefix) 
    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """


def get_faculty_id():
    return """
    select id from faculty 
    where name = %s;
    """


def get_all_category_uri():
    return """
    select uri from category;
    """


def get_prefix_id():
    return """
    select id from prefix 
    where name = %s;
    """


def get_course_id():
    return """
    select id from course
    where uri = %s;
    """


def get_prerequisite_id():
    return """
    select id from prerequisite
    where fk_course = %s;
    """


def get_antirequisite_id():
    return """
    select id from antirequisite
    where fk_course = %s;
    """


def get_corequisite_id():
    return """
    select id from corequisite
    where fk_course = %s;
    """


def insert_prerequisite():
    return """
    insert into prerequisite (id, fk_course)
    values (%s, %s);
    """


def insert_antirequisite():
    return """
    insert into antirequisite (id, fk_course)
    values (%s, %s);
    """


def insert_corequisite():
    return """
    insert into corequisite (id, fk_course)
    values (%s, %s);
    """


def insert_course_prerequisite():
    return """
    insert into course_prerequisite (id, fk_course, fk_prerequisite)
    values (%s, %s, %s);
    """


def insert_course_antirequisite():
    return """
    insert into course_antirequisite (id, fk_course, fk_antirequisite)
    values (%s, %s, %s);
    """


def insert_course_corequisite():
    return """
    insert into course_corequisite (id, fk_course, fk_corequisite)
    values (%s, %s, %s);
    """

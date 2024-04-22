import json
import os
import psycopg2
from psycopg2.extensions import connection

script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, 'database.config.json')

def database_connection() -> connection:

    with open(config_file_path, 'r') as file:
        config = json.load(file)

    connection = psycopg2.connect(
        host=config['host'],
        database=config['database'],
        user=config['user'],
        password=config['password']
    )

    return connection

def init_database():
    conn = database_connection()

    schema = {
        'faculty': 'create table faculty (id varchar(36) primary key, name text unique);',
        'category': 'create table category (id varchar(36) primary key, name text, url text);',
        'category_faculty': 'create table category_faculty (id varchar(36) primary key, fk_category varchar(36) references category(id), fk_faculty varchar(36) references faculty(id));',
        'prefix': 'create table prefix (id varchar(36) primary key, name varchar(4) unique, fk_category varchar(36) references category(id));',
        
        'program': 'create table program (id varchar(36) primary key, name text, url text, fk_faculty varchar(36) references faculty(id));',
        'course': 'create table course (id varchar(36) primary key, title text, description text, code text, url text, lower_liberal BOOLEAN, contract text, fk_prefix varchar(36) references prefix(id));',
        'program_course': 'create table program_course (id varchar(36) primary key, fk_program varchar(36) references program(id), fk_course varchar(36) references course(id), semester bigint);',
        
        'prerequisite': 'create table prerequisite (id varchar(36) primary key, fk_course varchar(36) references course(id));',
        'antirequisite': 'create table antirequisite (id varchar(36) primary key, fk_course varchar(36) references course(id));',
        'corequisite': 'create table corequisite (id varchar(36) primary key, fk_course varchar(36) references course(id));',

        'course_prerequisite': 'create table course_prerequisite (id varchar(36) primary key, fk_course varchar(36) references course(id), fk_prerequisite varchar(36) references prerequisite(id));',
        'course_antirequisite': 'create table course_antirequisite (id varchar(36) primary key, fk_course varchar(36) references course(id), fk_antirequisite varchar(36) references antirequisite(id));',
        'course_corequisite': 'create table course_corequisite (id varchar(36) primary key, fk_course varchar(36) references course(id), fk_corequisite varchar(36) references corequisite(id));',
    }

    for table, data in schema.items():
        conn.cursor().execute(data)
        print(f'Created table: {table}')
    
    conn.commit()

def drop_tables():
    sql = [
        'drop table category_faculty;',
        'drop table program_course;',
        'drop table program;',
        'drop table course_prerequisite;',
        'drop table course_antirequisite;',
        'drop table course_corequisite;',
        'drop table corequisite;',
        'drop table prerequisite;',
        'drop table antirequisite;',
        'drop table course;',
        'drop table prefix;',
        'drop table category;',
        'drop table faculty'
    ]

    conn = database_connection()
    for command in sql:
        conn.cursor().execute(command)

    conn.commit()        

def insert_faculty(id: str, name: str) -> str:
    return f"INSERT INTO faculty (id, name) VALUES ('{id}', '{name}');"

def insert_category(id: str, name: str, url: str) -> str:
    return f"INSERT INTO category (id, name, url) VALUES ('{id}', '{name}', '{url}');"

def insert_category_faculty(id: str, fk_category: str, fk_faculty: str) -> str:
    return f"INSERT INTO category_faculty (id, fk_category, fk_faculty) VALUES ('{id}', '{fk_category}', '{fk_faculty}');"

def insert_prefix(id: str, name: str, fk_category: str) -> str:
    return f"INSERT INTO prefix (id, name, fk_category) VALUES ('{id}', '{name}', '{fk_category}');"

def insert_program(id: str, name: str, url: str, fk_faculty: str) -> str:
    return f"INSERT INTO program (id, name, url, fk_faculty) VALUES ('{id}', '{name}', '{url}', '{fk_faculty}');"

def insert_course(id: str, title: str, description: str, code: str, url: str, lower_liberal: bool, contract: str, fk_prefix: str) -> str:
    return f"INSERT INTO course (id, title, description, code, url, lower_liberal, contract, fk_prefix) VALUES ('{id}', '{title}', '{description}', '{code}', '{url}', {lower_liberal}, '{contract}', '{fk_prefix}');"

def insert_program_course(id: str, fk_program: str, fk_course: str, semester: int) -> str:
    return f"INSERT INTO program_course (id, fk_program, fk_course, semester) VALUES ('{id}', '{fk_program}', '{fk_course}', {semester});"

def insert_prerequisite(id: str, fk_course: str) -> str:
    return f"INSERT INTO prerequisite (id, fk_course) VALUES ('{id}', '{fk_course}');"

def insert_antirequisite(id: str, fk_course: str) -> str:
    return f"INSERT INTO antirequisite (id, fk_course) VALUES ('{id}', '{fk_course}');"

def insert_corequisite(id: str, fk_course: str) -> str:
    return f"INSERT INTO corequisite (id, fk_course) VALUES ('{id}', '{fk_course}');"

def insert_course_prerequisite(id: str, fk_course: str, fk_prerequisite: str) -> str:
    return f"INSERT INTO course_prerequisite (id, fk_course, fk_prerequisite) VALUES ('{id}', '{fk_course}', '{fk_prerequisite}');"

def insert_course_antirequisite(id: str, fk_course: str, fk_antirequisite: str) -> str:
    return f"INSERT INTO course_antirequisite (id, fk_course, fk_antirequisite) VALUES ('{id}', '{fk_course}', '{fk_antirequisite}');"

def insert_course_corequisite(id: str, fk_course: str, fk_corequisite: str) -> str:
    return f"INSERT INTO course_corequisite (id, fk_course, fk_corequisite) VALUES ('{id}', '{fk_course}', '{fk_corequisite}');"


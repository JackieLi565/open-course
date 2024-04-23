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
    types = {
        'liberal': "create type liberal as enum ('LL', 'UL');"
    }

    schema = {
        'faculty': 'create table faculty (id varchar(36) primary key, name text unique);',
        'category': 'create table category (id varchar(36) primary key, name text, uri text);',
        'category_faculty': 'create table category_faculty (id varchar(36) primary key, fk_category varchar(36) references category(id), fk_faculty varchar(36) references faculty(id));',
        'prefix': 'create table prefix (id varchar(36) primary key, name varchar(4) unique, fk_category varchar(36) references category(id));',
        
        'program': 'create table program (id varchar(36) primary key, name text, uri text, fk_faculty varchar(36) references faculty(id));',
        'course': 'create table course (id varchar(36) primary key, title text, description text, code text, uri text, lib liberal, lecture real, lab real, weight real, count real, fk_prefix varchar(36) references prefix(id));',
        'program_course': 'create table program_course (id varchar(36) primary key, fk_program varchar(36) references program(id), fk_course varchar(36) references course(id), semester bigint);',
        
        'prerequisite': 'create table prerequisite (id varchar(36) primary key, fk_course varchar(36) references course(id));',
        'antirequisite': 'create table antirequisite (id varchar(36) primary key, fk_course varchar(36) references course(id));',
        'corequisite': 'create table corequisite (id varchar(36) primary key, fk_course varchar(36) references course(id));',

        'course_prerequisite': 'create table course_prerequisite (id varchar(36) primary key, fk_course varchar(36) references course(id), fk_prerequisite varchar(36) references prerequisite(id));',
        'course_antirequisite': 'create table course_antirequisite (id varchar(36) primary key, fk_course varchar(36) references course(id), fk_antirequisite varchar(36) references antirequisite(id));',
        'course_corequisite': 'create table course_corequisite (id varchar(36) primary key, fk_course varchar(36) references course(id), fk_corequisite varchar(36) references corequisite(id));',
    }

    conn = database_connection()
    curr = conn.cursor()

    for type_, data in types.items():
        curr.execute(data)
        print(f'Created type: {type_}')

    print()
    
    for table, data in schema.items():
        curr.execute(data)
        print(f'Created table: {table}')
    
    conn.commit()
    conn.close()
    curr.close()

def drop_types():
    types = [
        'drop type liberal'
    ]

    conn = database_connection()
    curr = conn.cursor()

    for command in types:
        curr.execute(command)

    conn.commit()
    conn.close()
    curr.close()     

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
    curr = conn.cursor()

    for command in sql:
        curr.execute(command)

    conn.commit()
    conn.close()
    curr.close()     

def insert_faculty(id: str, name: str) -> str:
    return f"insert into faculty (id, name) values ('{id}', '{name}');"

def insert_category(id: str, name: str, uri: str) -> str:
    return f"insert into category (id, name, uri) values ('{id}', '{name}', '{uri}');"

def insert_category_faculty(id: str, fk_category: str, fk_faculty: str) -> str:
    return f"insert into category_faculty (id, fk_category, fk_faculty) values ('{id}', '{fk_category}', '{fk_faculty}');"

def insert_prefix(id: str, name: str, fk_category: str) -> str:
    return f"insert into prefix (id, name, fk_category) values ('{id}', '{name}', '{fk_category}');"

def insert_program(id: str, name: str, uri: str, fk_faculty: str) -> str:
    return f"insert into program (id, name, uri, fk_faculty) values ('{id}', '{name}', '{uri}', '{fk_faculty}');"

def insert_course(id: str, title: str, description: str, code: str, uri: str, lib: str, lecture: float, lab: float, weight: float, count: float, fk_prefix: str) -> str:
    return f"insert into course (id, title, description, code, uri, lib, lecture, lab, weight, count, fk_prefix) values ('{id}', '{title}', '{description}', '{code}', '{uri}', '{lib}', {lecture}, {lab}, {weight}, {count}, '{fk_prefix}');"

def insert_program_course(id: str, fk_program: str, fk_course: str, semester: int) -> str:
    return f"insert into program_course (id, fk_program, fk_course, semester) values ('{id}', '{fk_program}', '{fk_course}', {semester});"

def insert_prerequisite(id: str, fk_course: str) -> str:
    return f"insert into prerequisite (id, fk_course) values ('{id}', '{fk_course}');"

def insert_antirequisite(id: str, fk_course: str) -> str:
    return f"insert into antirequisite (id, fk_course) values ('{id}', '{fk_course}');"

def insert_corequisite(id: str, fk_course: str) -> str:
    return f"insert into corequisite (id, fk_course) values ('{id}', '{fk_course}');"

def insert_course_prerequisite(id: str, fk_course: str, fk_prerequisite: str) -> str:
    return f"insert into course_prerequisite (id, fk_course, fk_prerequisite) values ('{id}', '{fk_course}', '{fk_prerequisite}');"

def insert_course_antirequisite(id: str, fk_course: str, fk_antirequisite: str) -> str:
    return f"insert into course_antirequisite (id, fk_course, fk_antirequisite) values ('{id}', '{fk_course}', '{fk_antirequisite}');"

def insert_course_corequisite(id: str, fk_course: str, fk_corequisite: str) -> str:
    return f"insert into course_corequisite (id, fk_course, fk_corequisite) values ('{id}', '{fk_course}', '{fk_corequisite}');"

def get_faculty_id(name: str) -> str:
    return f"select id from faculty where name = '{name}';"

def get_all_category_uri():
    return "select uri from category;"
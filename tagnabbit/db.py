# -*- coding: iso-8859-1 -*-

import shelve

from . import dbsqlite
from . import search

conn = None
faculty_db = None
projects_db = None

def load(filename):
    global conn, faculty_db, projects_db
    
    faculty_db = dbsqlite.SQLhash(filename, tablename='faculty')
    faculty_db.close()
    
    projects_db = dbsqlite.SQLhash(filename, tablename='projects')
    conn = projects_db.conn
    faculty_db.conn = conn

    faculty_db = shelve.Shelf(faculty_db)
    projects_db = shelve.Shelf(projects_db)

    return faculty_db.values(), projects_db.values()

def commit():
    conn.commit()

def add_faculty(f, add_to_search=True):
    key = str(f.id)
    faculty_db[key] = f
    commit()

    if add_to_search:
        index = search.get_index()
        writer = index.writer()
        search.update_faculty_record(writer, f)
        writer.commit()

def add_project(p, add_to_search=True):
    key = str(p.id)
    projects_db[key] = p
    commit()

    if add_to_search:
        index = search.get_index()
        writer = index.writer()
        search.update_project_record(writer, p)
        writer.commit()

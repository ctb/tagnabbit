import shelve

from . import dbsqlite

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

def add_faculty(f):
    print 'ADDING FACULTY', f.id, f.last_name
    key = str(f.id)
    faculty_db[key] = f
    commit()

def add_project(p):
    key = str(p.id)
    projects_db[key] = p
    commit()

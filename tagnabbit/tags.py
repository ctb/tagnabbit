# -*- coding: iso-8859-1 -*-
from . import db

faculty_by_tags = {}
all_faculty = {}

projects_by_tags = {}
all_projects = {}

def reset():
    global faculty_by_tags, all_faculty
    faculty_by_tags = {}
    all_faculty = {}

def load(filename):
    all_f, all_p = db.load('foo.sqlite')
    if (all_f or all_p):
        print 'LOADING'
        for f in all_f:
            add_or_update_faculty(f)
        for p in all_p:
            add_or_update_project(p)


def add_or_update_faculty(faculty):
    taglist = faculty.tags
    
    # clean out of existing tags
    for k, v in faculty_by_tags.items():
        if faculty in v:
            v.remove(faculty)

    # add back in
    for tag in taglist:
        x = faculty_by_tags.get(tag, [])
        x.append(faculty)
        faculty_by_tags[tag] = x

    # set ID & add to list, if DNE
    if faculty.id is None:
        next_id = 0
        if all_faculty:
            next_id = max(all_faculty.keys()) + 1

        faculty.id = next_id
        
    all_faculty[faculty.id] = faculty

    # save to DB.
    db.add_faculty(faculty)

def get_faculty_by_tags(taglist):
    if not taglist:
        return

    assert not isinstance(taglist, str)
    s = set(faculty_by_tags.get(taglist[0], []))
    
    for tag in taglist:
        x = faculty_by_tags.get(tag, [])
        s.intersection_update(set(x))

    return list(s)

def get_all_faculty():
    return list(all_faculty.values())

def get_faculty_member(id):
    return all_faculty[id]

def get_all_tags():
    x = list(faculty_by_tags)
    y = list(projects_by_tags)
    x.extend(y)
    return x

def get_tags_for_faculty(f):
    x = []
    for k, v in faculty_by_tags.items():
        if f in v:
            x.append(k)
    return x

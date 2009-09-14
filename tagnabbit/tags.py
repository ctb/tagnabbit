faculty_by_tags = {}
all_faculty = []

def reset():
    global faculty_by_tags, all_faculty
    faculty_by_tags = {}
    all_faculty = []

def add_faculty(faculty, taglist):
    assert not isinstance(taglist, str)
    for tag in taglist:
        x = faculty_by_tags.get(tag, [])
        x.append(faculty)
        faculty_by_tags[tag] = x

    faculty.id = len(all_faculty)
    all_faculty.append(faculty)

def get_faculty_by_tags(taglist):
    if not taglist:
        return

    assert not isinstance(taglist, str)
    s = set(faculty_by_tags.get(taglist[0], []))
    
    for tag in taglist:
        x = faculty_by_tags.get(tag, [])
        s.intersection_update(set(x))

    return s

def get_all_faculty():
    return list(all_faculty)

def get_tags_for_faculty(f):
    x = []
    for k, v in faculty_by_tags.items():
        if f in v:
            x.append(k)
    return x

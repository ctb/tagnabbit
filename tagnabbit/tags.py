faculty_by_tags = {}

def reset():
    global faculty_by_tags
    faculty_by_tags = {}

def add_faculty(faculty, taglist):
    assert not isinstance(taglist, str)
    for tag in taglist:
        x = faculty_by_tags.get(tag, [])
        x.append(faculty)
        faculty_by_tags[tag] = x

def get_faculty_by_tags(taglist):
    if not taglist:
        return

    assert not isinstance(taglist, str)
    s = set(faculty_by_tags.get(taglist[0], []))
    
    for tag in taglist:
        x = faculty_by_tags.get(tag, [])
        s.intersection_update(set(x))

    return s

import os
import shutil

import traceback

from whoosh import store, fields, index
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage

INDEXFILE='whoosh.index'
SCHEMA = fields.Schema(id=fields.ID(stored=True, unique=True),
                       record_type=fields.TEXT(stored=True), # proj/faculty
                       project_title=fields.TEXT,            # proj only
                       first_name=fields.TEXT,               # faculty only
                       last_name=fields.TEXT,                # faculty only
                       blurb=fields.TEXT,
                       url=fields.TEXT,
                       tags=fields.KEYWORD(lowercase=True, commas=True,
                                           scorable=True))

def get_index(force_create=False):
    location = INDEXFILE

    if force_create:
        print 'removing...', location
        if os.path.exists(location):
            shutil.rmtree(location)

    if not os.path.exists(location):
        print 'creating...', location
        os.mkdir(location)
    
        storage = FileStorage(location)
        ix = storage.create_index(schema=SCHEMA)
    else:
        storage = FileStorage(location)
        ix = storage.open_index()
        
    return ix

def build_index(dbfile):
    from . import db
    facultylist, projectlist = db.load(dbfile)

    ix = get_index(force_create=True)
    writer = ix.writer()
    
    for f in facultylist:
        print f.id, f.last_name
        update_faculty_record(writer, f, new_record=True)

    for p in projectlist:
        update_project_record(writer, p, new_record=True)

    writer.commit()

def update_faculty_record(writer, f):
    writer.update_document(id=unicode(f.id), first_name=f.first_name,
                           last_name=f.last_name, blurb=f.blurb, url=f.url,
                           tags=u",".join(f.tags), record_type=u'faculty')

def update_project_record(writer, p):
    writer.update_document(id=unicode(p.id), project_title=p.title,
                           blurb=p.blurb, url=p.url, tags=u",".join(p.tags),
                           record_type=u'project')
       
def search(query):
    ix = get_index()
    searcher = ix.searcher()

    hits = []
    try:
        hits = searcher.find("blurb", query)
    except:
        traceback.print_exc()

    return hits

if __name__ == '__main__':
    import sys
    dbfile = sys.argv[1]

    build_index(dbfile)
    print 'built whoosh search index'

    if len(sys.argv) > 2:
        query = unicode(sys.argv[2])
        hits = search(query)
        print '%d hits for query "%s":' % (len(hits), query)
        for h in hits:
            print h['id']

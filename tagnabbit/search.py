import os
import shutil

import traceback

from whoosh import store, fields, index
from whoosh.index import create_in
from whoosh.qparser import QueryParser
from whoosh.filedb.filestore import FileStorage
from whoosh.analysis import StemmingAnalyzer
from whoosh.query import Variations

INDEXFILE='whoosh.index'
SCHEMA = fields.Schema(id=fields.ID(stored=True, unique=True),
                       record_type=fields.TEXT(stored=True), # proj/faculty
                       project_title=fields.TEXT(analyzer=StemmingAnalyzer()),            # proj only
                       first_name=fields.TEXT,               # faculty only
                       last_name=fields.TEXT,                # faculty only
                       blurb=fields.TEXT(analyzer=StemmingAnalyzer()),
                       url=fields.TEXT,
                       tags=fields.KEYWORD(lowercase=True, commas=True,
                                           scorable=True))

def get_index(force_create=False):
    location = INDEXFILE

    if force_create:
        print 'removing search index:', location
        if os.path.exists(location):
            shutil.rmtree(location)

    if not os.path.exists(location):
        print 'creating search index:', location
        os.mkdir(location)
    
        storage = FileStorage(location)
        ix = storage.create_index(schema=SCHEMA)
    else:
        storage = FileStorage(location)
        ix = storage.open_index()
        
    return ix

def build_index():
    from . import db
    facultylist, projectlist = db.faculty_db.values(), db.projects_db.values()

    ix = get_index(force_create=True)
    writer = ix.writer()
    
    for f in facultylist:
        update_faculty_record(writer, f)

    for p in projectlist:
        update_project_record(writer, p)
        
    writer.commit()

def update_faculty_record(writer, f):
    # add first, last names, and tags to default search
    blurb = f.blurb
    x = [ f.first_name, f.last_name ] + f.tags
    blurb += u" " + u" ".join(x)
    
    writer.update_document(id=unicode(f.id), first_name=f.first_name,
                           last_name=f.last_name, blurb=blurb, url=f.url,
                           tags=u",".join(f.tags), record_type=u'faculty')

def update_project_record(writer, p):
    # add title & tags to default search
    blurb = p.blurb
    x = [ p.title ] + p.tags
    blurb += u" ".join(x)
    
    writer.update_document(id=unicode(p.id), project_title=p.title,
                           blurb=blurb, url=p.url, tags=u",".join(p.tags),
                           record_type=u'project')
       
def search(query):
    ix = get_index()
    searcher = ix.searcher()

    qp = QueryParser("blurb", schema=ix.schema, termclass=Variations)

    hits = []
    try:
        parsed = qp.parse(query)
        hits = searcher.search(parsed)
    except:
        traceback.print_exc()

    return hits

if __name__ == '__main__':
    import sys
    dbfile = sys.argv[1]

    #build_index(dbfile)
    from . import tags
    tags.load(dbfile)
    build_index()

    if len(sys.argv) > 2:
        query = unicode(sys.argv[2])
        hits = search(query)
        print '%d hits for query "%s":' % (len(hits), query)
        for h in hits:
            print h['id'], h['record_type']
            
            from . import db
            f = db.faculty_db[h['id']]
            print f.first_name, f.last_name
            

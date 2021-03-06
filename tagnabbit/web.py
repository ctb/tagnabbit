# -*- coding: iso-8859-1 -*-
import os.path
from optparse import OptionParser
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler
from quixote.server.simple_server import run as run_simple_server

import pkg_resources
pkg_resources.require('quixote >= 2.6')
pkg_resources.require('jinja2')

import quixote
from quixote.directory import Directory
from quixote.publish import Publisher
from quixote.util import StaticDirectory

import jinja2

###

def cmp_tags(a, b):
    return cmp(a.upper(), b.upper())

def cmp_faculty(a, b):
    return cmp(a.last_name.upper(), b.last_name.upper())

def cmp_projects(a, b):
    return cmp(a.title.upper(), b.title.upper())

###

from . import tags, objects, db, search

### set up jinja templates

thisdir = os.path.dirname(__file__)
templatesdir = os.path.join(thisdir, 'templates')
templatesdir = os.path.abspath(templatesdir)

loader = jinja2.FileSystemLoader(templatesdir)
env = jinja2.Environment(loader=loader)

def render_jinja2(t, d):
    e = {}
    for k, v in d.items():
        if isinstance(v, str):
            e[k] = unicode(v)
        else:
            e[k] = v

    return t.render(e)

###

class TopDirectory(Directory):
    _q_exports = ['', 'css', 'img', 'example', 'faculty', 'add_faculty',
                  'display_by_tag', 'f', 'p', 'projects', 'add_project',
                  'export_faculty', 'search']
    
    css = StaticDirectory(os.path.join(templatesdir, 'css'), use_cache=True)
    img = StaticDirectory(os.path.join(templatesdir, 'img'), use_cache=True)

    def _q_index(self):
        request = quixote.get_request()
        form = request.form

        hits = []
        hit_result = ""
        
        if 'q' in form:
            q = form['q']
            hits = search.search(unicode(q))

            resolved_hits = []
            for hit in hits:
                str_id = hit['id']
                if hit['record_type'] == 'faculty':
                    obj = db.faculty_db[str_id]
                    name = "Dr. %s %s" % (obj.first_name, obj.last_name)
                    url = './f?id=%s' % str_id
                elif hit['record_type'] == 'project':
                    obj = db.projects_db[str_id]
                    name = obj.title
                    url = './p?id=%s' % str_id
                else:
                    url = None
                    name = None
                    obj = None
                resolved_hits.append((url, name, obj))

            hits = resolved_hits

            hit_result = "%d matches in project and faculty blurbs" % len(hits)

            print 'DID SEARCH:', len(hits)
            
        taglist = tags.get_all_tags()
        taglist.sort(cmp_tags)

        search_tab = True
        page_title = "Search by tag"
        
        template = env.get_template('search.html')
        return render_jinja2(template, locals())

    def export_faculty(self):
        request = quixote.get_request()
        response = request.response

        response.set_content_type('text/plain')
        faculty_list = tags.get_all_faculty()

        def fix_url(u):
            if u and u.strip() and u != 'http://None':
                if not u.startswith('http'):
                    u = 'http://' + u
            else:
                u = ''
            return u

        for f in faculty_list:
            f.first_name = f.first_name.strip()
            f.last_name = f.last_name.strip()
            f.url = fix_url(f.url)
            tags.add_or_update_faculty(f)

        l = [ (f.first_name, f.last_name, fix_url(f.url)) for f in faculty_list ]
        l = [ ",".join(x) for x in l ]
        return "\r\n".join(l)

    def example(self):
        page_title = "Example page"
        template = env.get_template('example.html')
        return render_jinja2(template, locals())

    def faculty(self):
        request = quixote.get_request()
        taglist = request.form.get('tags', None)

        if taglist:
            taglist = taglist.split(',')
            faculty_list = tags.get_faculty_by_tags(taglist)
        else:
            faculty_list = tags.get_all_faculty()

        faculty_list.sort(cmp_faculty)

        page_title = "Faculty listing"
        faculty_tab = True

        template = env.get_template('faculty.html')
        return render_jinja2(template, locals())

    def projects(self):
        request = quixote.get_request()
        taglist = request.form.get('tags', None)

        if taglist:
            taglist = taglist.split(',')
            project_list = tags.get_projects_by_tags(taglist)
        else:
            project_list = tags.get_all_projects()

        project_list.sort(cmp_projects)

        page_title = "Projects listing"
        projects_tab = True

        template = env.get_template('projects.html')
        return render_jinja2(template, locals())

    def add_faculty(self):
        request = quixote.get_request()
        form = request.form

        already_exists = False
        submit_button_name = 'submit new faculty information'
        id = form.get('id', '')
        first_name = last_name = url = blurb = taglist = ''

        f = None
        if id:
            already_exists = True
            submit_button_name = 'update faculty information'

            id = int(id)
            f = tags.get_faculty_member(id)

            first_name = f.first_name
            last_name = f.last_name
            url = f.url
            blurb = f.blurb
            taglist = ", ".join(f.tags)
        
        first_name = form.get('first_name', first_name)
        if isinstance(first_name, str):
            first_name = first_name.decode('8859')
        first_name = first_name.strip()
        
        last_name = form.get('last_name', last_name)
        if isinstance(last_name, str):
            last_name = last_name.decode('8859')
        last_name = last_name.strip()
        
        url = form.get('url', url)
        if isinstance(url, str):
            url = url.decode('8859')
        
        blurb = form.get('blurb', blurb)
        if isinstance(blurb, str):
            blurb = blurb.decode('8859')
        
        taglist = form.get('tags', taglist)
        taglist = [ t.strip() for t in taglist.split(',') ]

        if form.get('submit') == submit_button_name \
           and first_name and last_name:
            if f:
                f.first_name = first_name
                f.last_name = last_name
                f.url = url
                f.blurb = blurb
                f.tags = taglist
            else:
                f = objects.Faculty(first_name, last_name, blurb, url)
                f.tags = taglist

            tags.add_or_update_faculty(f)
            
            return request.response.redirect(request.get_url(1) + '/')

        page_title = "Adding/editing faculty information"
        taglist = ", ".join(taglist)
        template = env.get_template('add_faculty.html')
        return render_jinja2(template, locals())

    def add_project(self):
        request = quixote.get_request()
        form = request.form

        already_exists = False
        submit_button_name = 'submit new project information'
        id = form.get('id', '')
        title = url = blurb = taglist = facultylist = ''

        p = None
        if id:
            already_exists = True
            submit_button_name = 'update project information'

            id = int(id)
            p = tags.get_project(id)

            title = p.title
            url = p.url
            blurb = p.blurb
            taglist = ", ".join(p.tags)
            facultylist = ", ".join(p.faculty)
        
        title = form.get('title', title)
        if isinstance(title, str):
            title = title.decode('8859')
        title = title.strip()
        
        url = form.get('url', url)
        if isinstance(url, str):
            url = url.decode('8859')
        
        blurb = form.get('blurb', blurb)
        if isinstance(blurb, str):
            blurb = blurb.decode('8859')
        
        taglist = form.get('tags', taglist)
        taglist = [ t.strip() for t in taglist.split(',') ]

        facultylist = form.get('faculty', facultylist)
        facultylist = [ t.strip() for t in facultylist.split(',') ]

        if form.get('submit') == submit_button_name and title:
            if p:
                p.title = title
                p.url = url
                p.blurb = blurb
                p.tags = taglist
                p.faculty = facultylist
            else:
                p = objects.Project(title, blurb, url)
                p.tags = taglist
                p.faculty = facultylist

            tags.add_or_update_project(p)
            
            return request.response.redirect(request.get_url(1) + '/')

        taglist = ", ".join(taglist)
        facultylist = ", ".join(facultylist)

        all_faculty = tags.get_all_faculty()
        all_faculty.sort(cmp_faculty)
        
        page_title = "Adding/editing project information"
        template = env.get_template('add_project.html')
        return render_jinja2(template, locals())

    def display_by_tag(self):
        request = quixote.get_request()
        form = request.form

        taglist = form.get('tags')
        taglist = taglist.split(',')
        taglist = [ x.strip() for x in taglist ]

        faculty_list = tags.get_faculty_by_tags(taglist)
        projects_list = tags.get_project_by_tags(taglist)

        faculty_list.sort(cmp_faculty)
        projects_list.sort(cmp_projects)

        page_title = "%s" % (",".join(taglist),)
        template = env.get_template('display_all.html')
        return render_jinja2(template, locals())

    def f(self):
        request = quixote.get_request()
        form = request.form

        id = form['id']
        id = int(id)

        faculty = tags.get_faculty_member(id)
        faculty_list = tags.get_all_faculty()

        prev_id = id - 1
        if prev_id < 0:
            prev_id = len(faculty_list) - 1

        next_id = id + 1
        while next_id >= len(faculty_list):
            next_id %= len(faculty_list)

        taglist = tags.get_tags_for_faculty(faculty)

        page_title = "Faculty page: %s %s" % (faculty.first_name,
                                              faculty.last_name,)

        if faculty.url and not faculty.url.startswith('http:'):
            faculty.url = 'http://' + faculty.url
            
        template = env.get_template('single_faculty.html')
        return render_jinja2(template, locals())

    def p(self):
        request = quixote.get_request()
        form = request.form

        id = form['id']
        id = int(id)

        project = tags.get_project(id)
        project_list = tags.get_all_projects()

        prev_id = id - 1
        if prev_id < 0:
            prev_id = len(project_list) - 1

        next_id = id + 1
        while next_id >= len(project_list):
            next_id %= len(project_list)

        taglist = tags.get_tags_for_project(project)
        facultylist = tags.get_faculty_for_project(project)

        page_title = "Project page: %s" % (project.title,)
        template = env.get_template('single_project.html')
        return render_jinja2(template, locals())

def create_publisher():
    # sets global Quixote publisher
    Publisher(TopDirectory(), display_exceptions='plain')

    # return a WSGI wrapper for the Quixote Web app.
    app = quixote.get_wsgi_app()
    app.publisher.is_thread_safe = True
    return app

def run_wsgi(port=8123):
    server = WSGIServer(('', port), WSGIRequestHandler)
    app = create_publisher()
    server.set_app(app)

    print 'serving on %s:%d' % (interface, port,)
    server.serve_forever()


def run(interface, port):
    print 'serving on %s:%d' % (interface, port,)
    run_simple_server(create_publisher, interface, port)


if __name__ == '__main__':
    import sys
    parser = OptionParser()

    parser.add_option('-i', '--interface', dest='interface',
                      help='interface to bind', default='localhost')
    parser.add_option('-p', '--port', dest='port', help='port to bind',
                      type='int', default='8123')
    
    (options, args) = parser.parse_args()
    dbfile=args[0]

    ##

    tags.load(dbfile)
    from . import search
    search.build_index()
    run(options.interface, options.port)

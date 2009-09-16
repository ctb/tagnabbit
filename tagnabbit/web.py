import os.path
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

import pkg_resources
pkg_resources.require('quixote >= 2.6')
pkg_resources.require('jinja2')

import quixote
from quixote.directory import Directory
from quixote.publish import Publisher
from quixote.util import StaticDirectory

import jinja2

###

from . import tags, objects, db

all_f, all_p = db.load('foo.sqlite')
if not (all_f or all_p):
    pass
else:
    print 'LOADING'
    for f in all_f:
        tags.add_faculty(f, f.tags)
    for p in all_p:
        tags.add_project(p, p.tags)

### set up jinja templates

thisdir = os.path.dirname(__file__)
templatesdir = os.path.join(thisdir, 'templates')
templatesdir = os.path.abspath(templatesdir)

loader = jinja2.FileSystemLoader(templatesdir)
env = jinja2.Environment(loader=loader)

###

class TopDirectory(Directory):
    _q_exports = ['', 'css', 'img', 'example', 'faculty', 'add_faculty',
                  'display_by_tag', 'f', 'p', 'projects', 'add_project']
    css = StaticDirectory(os.path.join(templatesdir, 'css'), use_cache=True)
    img = StaticDirectory(os.path.join(templatesdir, 'img'), use_cache=True)

    def _q_index(self):
        taglist = tags.get_all_tags()
        
        template = env.get_template('search.html')
        return template.render(locals())

    def example(self):
        template = env.get_template('example.html')
        return template.render(locals())

    def faculty(self):
        request = quixote.get_request()
        taglist = request.form.get('tags', None)

        if taglist:
            taglist = taglist.split(',')
            faculty_list = tags.get_faculty_by_tags(taglist)
        else:
            faculty_list = tags.get_all_faculty()

        template = env.get_template('faculty.html')
        return template.render(locals())

    def add_faculty(self):
        request = quixote.get_request()
        form = request.form

        id = form.get('id', '')
        first_name = last_name = url = blurb = taglist = ''

        f = None
        if id:
            id = int(id)
            faculty_list = tags.get_all_faculty()
            f = faculty_list[id]

            first_name = f.first_name
            last_name = f.last_name
            url = f.url
            blurb = f.blurb
            taglist = ", ".join(f.tags)
        
        first_name = form.get('first_name', first_name)
        last_name = form.get('last_name', last_name)
        url = form.get('url', url)
        blurb = form.get('blurb', blurb)
        taglist = form.get('tags', taglist)
        taglist = [ t.strip() for t in taglist.split(',') ]

        if form.get('submit') == 'add' and first_name and last_name:
            if f:
                f.first_name = first_name
                f.last_name = last_name
                f.url = url
                f.blurb = blurb
                f.tags = taglist
                tags.update_faculty(f, taglist)
            else:
                f = objects.Faculty(first_name, last_name, blurb, url)
                f.tags = taglist
                tags.add_faculty(f, f.tags)

            db.add_faculty(f)
            return request.response.redirect(request.get_url(1))

        taglist = ", ".join(taglist)
        template = env.get_template('add_faculty.html')
        return template.render(locals())

    def display_by_tag(self):
        request = quixote.get_request()
        form = request.form

        taglist = form.get('tags', ['tagA'])
        taglist = taglist.split(',')
        taglist = [ x.strip() for x in taglist ]

        faculty_list = tags.get_faculty_by_tags(taglist)
        project_list = []

        template = env.get_template('display_all.html')
        return template.render(locals())

    def f(self):
        request = quixote.get_request()
        form = request.form

        id = form['id']
        id = int(id)

        faculty_list = tags.get_all_faculty()
        faculty = faculty_list[id]

        prev_id = id - 1
        if prev_id < 0:
            prev_id = len(faculty_list) - 1

        next_id = id + 1
        while next_id >= len(faculty_list):
            next_id %= len(faculty_list)

        taglist = tags.get_tags_for_faculty(faculty)

        template = env.get_template('single_faculty.html')
        return template.render(locals())

def create_publisher():
    # sets global Quixote publisher
    Publisher(TopDirectory(), display_exceptions='plain')

    # return a WSGI wrapper for the Quixote Web app.
    app = quixote.get_wsgi_app()
    app.publisher.is_thread_safe = True
    return app

def run(port=8123):
    server = WSGIServer(('', port), WSGIRequestHandler)
    app = create_publisher()
    server.set_app(app)

    print 'serving on port', port
    server.serve_forever()

if __name__ == '__main__':
    run()

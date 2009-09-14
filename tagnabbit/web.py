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

from . import tags, objects

f = objects.Faculty('foo', 'bar', '', '')
g = objects.Faculty('zip', 'zap', '', '')

tags.add_faculty(f, ['a', 'b'])
tags.add_faculty(g, ['a', 'c'])


### set up jinja templates

thisdir = os.path.dirname(__file__)
templatesdir = os.path.join(thisdir, 'templates')
templatesdir = os.path.abspath(templatesdir)

loader = jinja2.FileSystemLoader(templatesdir)
env = jinja2.Environment(loader=loader)

###

class TopDirectory(Directory):
    _q_exports = ['', 'css', 'img', 'example', 'faculty', 'add_faculty']
    css = StaticDirectory(os.path.join(templatesdir, 'css'), use_cache=True)
    img = StaticDirectory(os.path.join(templatesdir, 'img'), use_cache=True)

    def _q_index(self):
        content = "hello, world"
        
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

        first_name = form.get('first_name')
        last_name = form.get('last_name')
        url = form.get('url', 'some url')
        blurb = form.get('blurb', 'some blurb')
        taglist = form.get('taglist', 'a,b,c')

        if first_name and last_name:
            f = objects.Faculty(first_name, last_name, blurb, url)
            tags.add_faculty(f, taglist.split(','))
            return request.response.redirect(request.get_url(1))
        
        template = env.get_template('add_faculty.html')
        return template.render(locals())

def create_publisher():
    # sets global Quixote publisher
    Publisher(TopDirectory(), display_exceptions='plain')

    # return a WSGI wrapper for the Quixote Web app.
    app = quixote.get_wsgi_app()
    app.publisher.is_thread_safe = True
    return app

def run(port=8000):
    server = WSGIServer(('', port), WSGIRequestHandler)
    app = create_publisher()
    server.set_app(app)

    print 'serving on port', port
    server.serve_forever()

if __name__ == '__main__':
    run()

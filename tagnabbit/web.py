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

### set up jinja templates

thisdir = os.path.dirname(__file__)
templatesdir = os.path.join(thisdir, 'templates')
templatesdir = os.path.abspath(templatesdir)

loader = jinja2.FileSystemLoader(templatesdir)
env = jinja2.Environment(loader=loader)

###

class TopDirectory(Directory):
    _q_exports = ['', 'css', 'img', 'example']
    css = StaticDirectory(os.path.join(templatesdir, 'css'), use_cache=True)
    img = StaticDirectory(os.path.join(templatesdir, 'img'), use_cache=True)

    def _q_index(self):
        content = "hello, world"
        
        template = env.get_template('index.html')
        return template.render(locals())

    def example(self):
        template = env.get_template('example.html')
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

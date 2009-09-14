from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

import pkg_resources
pkg_resources.require('quixote >= 2.6')

import quixote
from quixote.directory import Directory
from quixote.publish import Publisher

class TopDirectory(Directory):
    _q_exports = ['']

    def _q_index(self):
        return "hello, world"

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

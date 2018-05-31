"""
Safely serve the log server app
http://flask.pocoo.org/docs/1.0/deploying/wsgi-standalone/#gevent
"""

from gevent.wsgi import WSGIServer
from logServer import app

http_server = WSGIServer(("", 80), app)
http_server.serve_forever()

import json
import logging
import os.path

from app import app
from app import database as db
from app import util
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

db.initialize()

logging.basicConfig(filename='actistairs.log', level=logging.INFO)
logging.info('starting actistairs application')

context = {
        'certfile': os.path.join('cert', 'wildcard.offis.de.crt'),
        'keyfile': os.path.join('cert', 'wildcard.offis.de.key'),
        }
http_server = HTTPServer(WSGIContainer(app))
http_server.listen(8443)
IOLoop.instance().start()
# app.run(host='srvg03.offis.uni-oldenburg.de', port=1026, debug=True)
# app.run(host='127.0.0.1', debug=True, ssl_context=context)
# app.run(host='127.0.0.1', debug=True)

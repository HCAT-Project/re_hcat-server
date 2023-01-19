import logging
import os.path
import sys
import threading

from flask import Flask, request
from gevent import pywsgi
from RPDB.database import RPDB

import util
from event.event_manager import EventManager
from event.recv_event import RecvEvent


class Server:
    def __init__(self, address: tuple[str, int] = None, debug: bool = False):
        self.app = Flask(__name__)
        self.host, self.port = address if address is not None else ('0.0.0.0', 8080)
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        self.key = util.get_random_token(16)
        self.db_account = RPDB(os.path.join('data', 'account'))
        self.e_mgr = EventManager(self)

    def server_thread(self):
        if self.debug:
            self.app.run(self.host, self.port, debug=True)
        else:
            server = pywsgi.WSGIServer((self.host, self.port), self.app)
            server.serve_forever()

    def start(self):
        self.logger.info('Starting server...')
        self.logger.info('Creating route...')

        @self.app.route('/api/<path:path>')
        def recv(path):
            return self.e_mgr.create_event(RecvEvent, request, path)

        self.logger.info('Starting server thread...')
        t_server = threading.Thread(target=self.server_thread, daemon=True, name='server_thread')
        t_server.start()
        self.logger.info('Server is already started.')
        while True:
            try:
                t_server.join(0.1)
            except KeyboardInterrupt:
                sys.exit()

    def open_user(self, user_id):
        return self.db_account.enter(user_id)


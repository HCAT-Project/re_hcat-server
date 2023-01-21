import logging
import os.path
import sys
import threading
import time

from flask import Flask, request
from gevent import pywsgi
from RPDB.database import RPDB

import util
from containers import User
from event.event_manager import EventManager
from event.recv_event import RecvEvent


class Server:
    def __init__(self, address: tuple[str, int] = None, debug: bool = False, name=__name__):
        # init Flask object
        self.app = Flask(__name__)
        # get the host and port from the address
        self.host, self.port = address if address is not None else ('0.0.0.0', 8080)
        # set debug mode
        self.debug = debug
        # get logger
        self.logger = logging.getLogger(__name__)
        # generate aes token
        if not os.path.exists(f'{name}.key'):
            self.key = util.get_random_token(16)
            with open(f'{name}.key', 'w', encoding='utf8') as f:
                f.write(self.key)
        else:
            with open(f'{name}.key', 'r', encoding='utf8') as f:
                self.key = f.read()

        # set event manager
        self.e_mgr = EventManager(self)
        # set timeout
        self.event_timeout = 604_800
        self.activity_dict = {}
        self.activity_dict_lock = threading.Lock()
        # init database
        self.db_account = RPDB(os.path.join('data', 'account'))
        self.db_event = RPDB(os.path.join('data', 'event'))

    def server_thread(self):

        # start wsgi server
        server = pywsgi.WSGIServer((self.host, self.port), self.app)
        server.serve_forever()

    def activity_list_thread(self):
        while True:
            del_list = []
            self.activity_dict_lock.acquire()
            for i in self.activity_dict:
                self.activity_dict[i] -= 1
                if self.activity_dict[i] <= 0:
                    del_list.append(i)
            for i in del_list:
                self.activity_dict.pop(i)
            self.activity_dict_lock.release()

            for i in del_list:
                with self.open_user(i) as u:
                    user: User = u.value
                    user.status = 'offline'
            time.sleep(1)

    def event_cleaner_thread(self):
        while True:
            for i in self.db_event.keys:
                with self.db_event.enter(i) as v:
                    # THERE IS NO BUG HERE!!!
                    # I don't understand why PyCharm think it is a bug
                    if time.time() - v.value['time'] > self.event_timeout:
                        # del event if event timeout
                        v.value = None
            time.sleep(30)

    def start(self):
        self.logger.info('Starting server...')
        self.logger.info('Creating route...')

        @self.app.route('/api/<path:path>')
        def recv(path):
            return self.e_mgr.create_event(RecvEvent, request, path)

        self.logger.info('Starting server thread...')
        t_server = threading.Thread(target=self.server_thread, daemon=True, name='server_thread')
        t_cleaner = threading.Thread(target=self.event_cleaner_thread, daemon=True, name='event_cleaner_thread')
        t_activity = threading.Thread(target=self.activity_list_thread, daemon=True, name='activity_thread')
        t_server.start()
        t_cleaner.start()
        t_activity.start()
        self.logger.info('Server is already started.')
        while True:
            try:
                t_server.join(0.1)
            except KeyboardInterrupt:
                sys.exit()

    def open_user(self, user_id):
        return self.db_account.enter(user_id)

    def is_user_exist(self, user_id):
        with self.open_user(user_id) as u:
            return u.value is not None

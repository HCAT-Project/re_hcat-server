import copy
import logging
import os.path
import platform
import sys
import threading
import time

from RPDB.database import RPDB
from flask import Flask, request
from flask_cors import CORS
from gevent import pywsgi

import util
from containers import User, EventContainer
from event.event_manager import EventManager
from event.recv_event import RecvEvent


class Server:
    ver = '2.0.1'

    def __init__(self, address: tuple[str, int] = None, debug: bool = False, name=__name__, config=None):
        # Initialize Flask object
        self.app = Flask(__name__)
        # Enable Cross-Origin Resource Sharing (CORS)
        CORS(self.app)

        # Set host and port for the server
        self.host, self.port = address if address is not None else ('0.0.0.0', 8080)

        # Set debug mode
        self.debug = debug

        # Initialize config
        self.config = {} if config is None else copy.deepcopy(config)

        # Get logger
        self.logger = logging.getLogger(__name__)

        # Generate AES token
        key_path = os.path.join(os.getcwd(), f'{name}.key')
        if not os.path.exists(key_path):
            self.key = util.get_random_token(16)
            with open(key_path, 'w', encoding='utf8') as f:
                f.write(self.key)
        else:
            with open(key_path, 'r', encoding='utf8') as f:
                self.key = f.read()

        # Set event manager
        self.e_mgr = EventManager(self)

        # Set timeout
        self.event_timeout = 604_800  # 1 week

        # Keep track of active users
        self.activity_dict = {}
        self.activity_dict_lock = threading.Lock()

        # Initialize databases
        self.db_account = RPDB(os.path.join(os.getcwd(), 'data', 'account'))
        self.db_event = RPDB(os.path.join(os.getcwd(), 'data', 'event'))
        self.db_group = RPDB(os.path.join(os.getcwd(), 'data', 'group'))

    def server_thread(self):
        # Start the WSGI server
        server = pywsgi.WSGIServer((self.host, self.port), self.app)
        server.serve_forever()

    def activity_list_thread(self):
        # Monitor the activity of users and mark them as offline if they are inactive
        while True:
            del_list = []
            with self.activity_dict_lock:
                for i in self.activity_dict:
                    self.activity_dict[i] -= 1
                    if self.activity_dict[i] <= 0:
                        del_list.append(i)
                for i in del_list:
                    self.activity_dict.pop(i)

            for i in del_list:
                with self.open_user(i) as u:
                    user: User = u.value
                    user.status = 'offline'
            time.sleep(1)

    def event_cleaner_thread(self):
        # Remove expired events from the event database
        while True:
            for i in self.db_event.keys:
                with self.db_event.enter(i) as v:
                    if v.value and time.time() - v.value['time'] > self.event_timeout:
                        v.value = None
            time.sleep(30)

    def start(self):
        # Log server start
        self.logger.info('Starting server...')

        # Create route for handling incoming requests
        self.logger.info('Creating route...')

        @self.app.route('/api/<path:path>', methods=['GET', 'POST'])
        def recv(path):
            return self.e_mgr.create_event(RecvEvent, request, path)

        # Start server threads
        self.logger.info('Starting server threads...')
        server_thread = threading.Thread(target=self.server_thread, daemon=True, name='server_thread')
        cleaner_thread = threading.Thread(target=self.event_cleaner_thread, daemon=True, name='event_cleaner_thread')
        activity_thread = threading.Thread(target=self.activity_list_thread, daemon=True, name='activity_thread')
        threads = [server_thread, cleaner_thread, activity_thread]
        for t in threads:
            t.start()

        # Log server status and information
        self.logger.info('Server started.')
        self.logger.info(f'Server listening on {self.host}:{self.port}.')
        self.logger.info('----Server information----')
        self.logger.info(f'Version: {self.ver}')
        self.logger.info(f'Python version: {sys.version}')
        self.logger.info(f'System version: {platform.platform()}')
        self.logger.info(f'Debug mode: {self.debug}')
        self.logger.info(f'Current working directory: {os.getcwd()}')
        self.logger.info('--------------------------')

        try:
            # Wait for the server thread to finish
            server_thread.join(0.1)
        except KeyboardInterrupt:
            sys.exit()

    def open_user(self, user_id):
        return self.db_account.enter(user_id)

    def is_user_exist(self, user_id):
        with self.open_user(user_id) as u:
            return u.value is not None

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : server.py

@Author     : hsn

@Date       : 2023/3/1 下午8:35

@Version    : 2.1.1
"""

#  Copyright (C) 2023. HCAT-Project-Team
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import copy
import importlib
import logging
import os.path
import platform
import socket
import sys
import threading
import time

from RPDB.database import FRPDB,RPDB
from flask import Flask, request, url_for, send_from_directory
from flask_cors import CORS
from gevent import pywsgi
from permitronix import Permitronix

from src import util
from src.containers import User, ReturnData
from src.event.event_manager import EventManager
from src.event.recv_event import RecvEvent
from src.util.i18n import gettext_func as _


class Server:
    ver = '2.2.0'

    def __init__(self, http_address: tuple[str, int] = None, tcp_address: tuple[str, int] = None, debug: bool = False,
                 name=__name__, config=None):
        # Initialize Flask object
        self.tcp_server_handle = None
        self.app = Flask(__name__)
        if debug:
            self.app.config['SESSION_COOKIE_SAMESITE'] = 'None'
            self.app.config['SESSION_COOKIE_SECURE'] = False

        # Enable Cross-Origin Resource Sharing (CORS)
        CORS(self.app, supports_credentials=True)

        # Set host and port for the server
        self.http_host, self.http_port = http_address if http_address is not None else ('0.0.0.0', 8080)
        self.tcp_host, self.tcp_port = tcp_address if tcp_address is not None else ('0.0.0.0', 29876)

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
        self.event_timeout = 7 * 24 * 60 * 60  # 1 week
        self.short_id_timeout = 5 * 60  # 5 minutes

        # Keep track of active users
        self.activity_dict = {}
        self.activity_dict_lock = threading.Lock()

        # Initialize databases
        self.db_account = FRPDB(os.path.join(os.getcwd(), 'data', 'account'))
        self.db_event = FRPDB(os.path.join(os.getcwd(), 'data', 'event'))
        self.db_group = FRPDB(os.path.join(os.getcwd(), 'data', 'group'))
        self.db_email = FRPDB(os.path.join(os.getcwd(), 'data', 'email'))
        self.db_permitronix = RPDB(os.path.join(os.getcwd(), 'data', 'permitronix'))

        self.event_sid_table = {}

        self.permitronix: Permitronix = Permitronix(self.db_permitronix)

    def http_server_thread(self):
        # Start the WSGI server
        server = pywsgi.WSGIServer((self.http_host, self.http_port), self.app)
        server.serve_forever()

    def tcp_server_thread(self):
        # Start the tcp server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.tcp_host, self.tcp_port))
        server.listen(255)
        while True:
            conn, addr = server.accept()
            threading.Thread(target=self.tcp_server_handle, args=(conn, addr)).start()

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
            del_e_count = 0
            del_sid_count = 0
            for i in copy.deepcopy(self.db_event.keys):
                with self.db_event.enter(i) as v:
                    e: dict = v.value
                    if e and time.time() - e['time'] > self.event_timeout:
                        v.value = None
                        del_e_count += 1

            for k, v in copy.deepcopy(self.event_sid_table).items():
                try:
                    allow_del = v not in self.db_event.keys or time.time() - self.get_user_event(v)[
                        'time'] > self.short_id_timeout
                except:
                    allow_del = True

                if allow_del:
                    self.event_sid_table.pop(k)
                    del_sid_count += 1

            if del_sid_count > 0 or del_e_count > 0:
                self.logger.info(_('Event cleaner: {} events deleted, {} short IDs deleted.')
                                 .format(del_e_count, del_sid_count))

            time.sleep(30)

    def load_auxiliary_events(self):
        # get all auxiliary events
        for name_ in os.listdir(os.path.join('src', 'event', 'auxiliary_events')):
            # get file name
            name = "".join(name_.split(".")[:-1])
            if len(name) == 0:
                continue

            # get class name
            class_name = ''
            for i in name.split("_"):
                if len(i) == 0:
                    continue
                class_name += i[0].upper() + ('' if len(i) < 2 else i[1:])

            # logout
            self.logger.debug(_('Auxiliary event "{}" loaded.').format(name))

            # import module and add event
            event_module = importlib.import_module(f'src.event.auxiliary_events.{name}')
            event_class = getattr(event_module, class_name)
            self.e_mgr.add_auxiliary_event(event_class.main_event, event_class)

    def start(self):
        # Log server start
        self.logger.info(_('Starting server...'))

        # Load auxiliary events
        self.logger.info(_('Loading auxiliary events...'))
        self.load_auxiliary_events()

        # Create route for handling incoming requests
        self.logger.info(_('Creating route...'))

        @self.app.route('/<path:path>', methods=['GET', 'POST'])
        def send_static(path):
            return send_from_directory(os.path.join(os.getcwd(),'static'), path)

        @self.app.route('/api/<path:path>', methods=['GET', 'POST'])
        def recv(path):
            rt = self.e_mgr.create_event(RecvEvent, request, path)
            # format return data
            if isinstance(rt, ReturnData):
                rt = rt.jsonify()
            elif rt is None:
                rt = ReturnData(ReturnData.NULL, '').jsonify()
            return rt

        # Create handler for handling incoming tcp requests
        self.logger.info(_('Creating tcp handler...'))

        def tcp_handler(conn, addr):
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    tcp_recv(conn, addr, data)
                except:
                    break
            conn.close()

        def tcp_recv(conn, addr, data):
            rt = self.e_mgr.create_event(RecvEvent, conn, addr, data)
            # format return data
            if isinstance(rt, ReturnData):
                rt = rt.jsonify()
            elif rt is None:
                rt = ReturnData(ReturnData.NULL, '').jsonify()
            conn.send(rt.encode('utf-8'))

        self.tcp_server_handle = tcp_handler

        # Start server threads
        self.logger.info(_('Starting server threads...'))
        server_thread = threading.Thread(target=self.http_server_thread, daemon=True, name='server_thread')
        cleaner_thread = threading.Thread(target=self.event_cleaner_thread, daemon=True, name='event_cleaner_thread')
        activity_thread = threading.Thread(target=self.activity_list_thread, daemon=True, name='activity_thread')
        threads = [server_thread, cleaner_thread, activity_thread]
        for t in threads:
            t.start()

        # Log server status and information
        self.logger.info(_('Server started.'))
        self.logger.info(_('Server listening on {}:{}.').format(self.http_host, self.http_port))
        self.logger.info(_('----Server information----'))
        self.logger.info(_('Version: {}').format(self.ver))
        self.logger.info(_('Python version: {}').format(sys.version))
        self.logger.info(_('System version: {}').format(platform.platform()))
        self.logger.info(_('Debug mode: {}').format(self.debug))
        self.logger.info(_('Current working directory: {}').format(os.getcwd()))
        if 'client' in self.config \
                and 'client-build' in self.config['client'] \
                and self.config['client']['client-build'] is not None:
            self.logger.info(_('Client build: {}').format(self.config['client']['client-build']))
        self.logger.info(_('--------------------------'))

        try:
            # Wait for the server thread to finish
            while True:
                server_thread.join(0.1)
        except KeyboardInterrupt:
            # save data and exit
            self.logger.info(_('Saving data...'))
            self.db_event.close()
            self.db_email.close()
            self.db_group.close()
            self.db_account.close()
            self.db_permitronix.close()
            try:
                sys.exit()
            except SystemExit:
                self.logger.info(_('Server closed.'))

    def open_user(self, user_id):
        return self.db_account.enter(user_id)

    def is_user_exist(self, user_id):
        with self.open_user(user_id) as u:
            return u.value is not None

    def get_user_event(self, event_id: str) -> dict:
        eid = copy.copy(event_id)

        if eid in self.event_sid_table:
            eid = self.event_sid_table[eid]

        with self.db_event.enter(eid) as e:
            return e.value

    def is_user_event_exist(self, event_id: str) -> bool:
        return self.get_user_event(event_id) is not None

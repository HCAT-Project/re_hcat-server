#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : server.py

@Author     : hsn

@Date       : 2023/3/1 下午8:35

@Version    : 2.1.1
"""

#  Copyright (C) 2023. HCAT-Project-Team
#  _
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  _
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  _
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import copy
import logging
import os.path
import platform
import sys
import threading
import time

from RPDB.database import FRPDB
import schedule
import src.util.crypto
import src.util.text
from src import util
from src.containers import User
from src.dynamic_class_loader import DynamicObjLoader
from src.event.event_manager import EventManager
from src.event.recv_event import RecvEvent
from src.util.config_parser import ConfigParser
from src.util.i18n import gettext_func as _
from src.util.file_manager import FileManager

''' markdown
> I believe that communication is our freedom and should not be controlled by any country, regime, or corporation.
>       -- hsn8086
'''


class Server:
    """
    The core of the server.
    """
    ver = '2.4.3'

    def __init__(self, debug: bool = False,
                 name=__name__, config=None, dol: DynamicObjLoader = None):
        """
        Initialize the server.
        :param debug:
        :param name: The name of server.
        :param config: Server config.
        :param dol: DynamicObjLoader.
        """
        # Get logger
        self.logger = logging.getLogger(__name__)

        # Create DynamicObjLoader
        self.logger.info(_('Creating DynamicObjLoader...'))
        if dol is None:
            self.dol = DynamicObjLoader()
        else:
            self.dol = dol

        # Set debug mode
        self.debug = debug

        # Initialize config
        self.logger.info(_('Loading config...'))
        self.config = ConfigParser({}) if config is None else ConfigParser(copy.deepcopy(config))

        # Generate AES token
        self.logger.info(_('Generating AES token...'))
        key_path = os.path.join(os.getcwd(), f'{name}.key')
        if not os.path.exists(key_path):
            self.key = src.util.crypto.get_random_token(16)
            with open(key_path, 'w', encoding='utf8') as f:
                f.write(self.key)
        else:
            with open(key_path, 'r', encoding='utf8') as f:
                self.key = f.read()

        # Set event manager
        self.e_mgr = EventManager(self)

        # Set timeout
        self.event_timeout = self.config.get_from_pointer('/sys/event-timeout', 7 * 24 * 60 * 60)  # 1 week
        self.short_id_timeout = self.config.get_from_pointer('/sys/sid-timeout', 5 * 60)  # 5 minutes

        # Keep track of active users
        self.activity_dict = {}
        self.activity_dict_lock = threading.Lock()

        # Initialize databases
        self.db_account = FRPDB(os.path.join(os.getcwd(), 'data', 'account'))
        self.db_event = FRPDB(os.path.join(os.getcwd(), 'data', 'event'))
        self.db_group = FRPDB(os.path.join(os.getcwd(), 'data', 'group'))
        self.db_email = FRPDB(os.path.join(os.getcwd(), 'data', 'email'))
        self.db_file_info = FRPDB(os.path.join(os.getcwd(), 'data', 'file_info'))
        # Initialize file manager
        self.upload_folder = FileManager(self.config.get_from_pointer('/network/upload/upload_folder', 'static/files'),
                                         self.db_file_info)

        # Initialize sid table
        self.event_sid_table = {}

    def request_handler(self, req):
        return self.e_mgr.create_event(RecvEvent, req, req.path)

    def _schedule_activity_list(self):
        # Monitor the activity of users and mark them as offline if they are inactive

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

    def _schedule_cleaner(self):
        # Remove expired events from the event database

        del_e_count = 0
        del_sid_count = 0
        for i in copy.deepcopy(self.db_event.keys):
            with self.db_event.enter(i) as v:
                assert isinstance(v.value, dict)
                e: dict = v.value
                if e and time.time() - e['time'] > self.event_timeout:
                    v.value = None
                    del_e_count += 1

        for k, v in copy.deepcopy(self.event_sid_table).items():
            try:
                allow_del = v not in self.db_event.keys or time.time() - self.get_user_event(v)[
                    'time'] > self.short_id_timeout
            except KeyError:
                allow_del = True

            if allow_del:
                self.event_sid_table.pop(k)
                del_sid_count += 1

        del_file_c = self.upload_folder.clear_timeout()
        if del_sid_count > 0 or del_e_count > 0 or del_file_c > 0:
            self.logger.info(_('Event cleaner: {} events deleted, {} short IDs deleted,{} files deleted.')
                             .format(del_e_count, del_sid_count, del_file_c))

    def start(self):
        # Start server threads
        self.logger.info(_('Starting scheduler...'))
        schedule.every(30).seconds.do(self._schedule_cleaner)
        schedule.every(1).seconds.do(self._schedule_activity_list)

        # Log server status and information
        self.logger.info(_('Server started.'))

        self.logger.info(_('----Server information----'))
        self.logger.info(_('Version: {}').format(self.ver))
        self.logger.info(_('Python version: {}').format(sys.version))
        self.logger.info(_('System version: {}').format(platform.platform()))
        self.logger.info(_('Debug mode: {}').format(self.debug))
        self.logger.info(_('Current working directory: {}').format(os.getcwd()))
        if 'client' in self.config \
                and 'client-branch' in self.config['client'] \
                and self.config['client']['client-branch'] is not None:
            self.logger.info(_('Client branch: {}').format(self.config['client']['client-branch']))
        self.logger.info(_('--------------------------'))

    def server_forever(self):
        self.start()
        while True:
            schedule.run_pending()
            time.sleep(0.1)

    def close(self):
        # save data and exit
        self.logger.info(_('Saving data...'))
        self.db_event.close()
        self.db_email.close()
        self.db_group.close()
        self.db_account.close()

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

    def check_file_exists(self, file_hash):
        upl_folder = self.config.get_from_pointer('/network/upload/upload_folder', default='static/files')
        return os.path.exists(os.path.join(upl_folder, file_hash))

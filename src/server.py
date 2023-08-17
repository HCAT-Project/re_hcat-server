#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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

"""
@File       : server.py

@Author     : hsn

@Date       : 2023/3/1 下午8:35

@Version    : 2.5.2
"""

import contextlib
import copy
import logging
import os.path
import platform
import sys
import time
from typing import Any, Mapping, Dict

import schedule

import src.util.crypto
import src.util.text
from src.containers import User, ReturnData, Request, Group
from src.db_adapter.base_dba import BaseDBA
from src.dynamic_obj_loader import DynamicObjLoader
from src.event.event_manager import EventManager
from src.event.recv_event import RecvEvent
from src.util.config_parser import ConfigParser
from src.util.crypto import get_random_token
from src.util.file_manager import FileManager
from src.util.i18n import gettext_func as _
from src.util.jelly import dehydrate, agar
from src.util.text import pascal_case_to_under_score

''' markdown
> I believe that communication is our freedom and should not be controlled by any country, regime, or corporation.
>       -- hsn8086
'''


class Server:
    """
    The core of the server.
    """
    ver = '2.5.2'

    def __init__(self, debug: bool = False,
                 name=__name__, config=None, dol=None):
        """
        Initialize the server.
        :param debug:
        :param name: The name of server.
        :param config: Server config.
        :param dol: DynamicObjLoader.
        """
        # Get logger
        self.running = True
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
        self.activity_dict: Dict[str, int] = {}

        # Get DBA
        dba_name = pascal_case_to_under_score(self.config.get_from_pointer('/db/use', 'Mongo'))
        self.dba: BaseDBA = self.dol.load_obj_from_group(dba_name, group='db_adapters')(config=self.config)

        # Initialize databases
        self.db_account = self.dba['account']
        self.db_event = self.dba['event']
        self.db_group = self.dba['group']
        self.db_email = self.dba['email']
        self.db_file_info = self.dba['file_info']

        # Initialize file manager
        self.upload_folder = FileManager(self.config.get_from_pointer('/network/upload/upload_folder', 'static/files'),
                                         self.db_file_info)

        # Initialize sid table
        self.event_sid_table: Dict[str, str] = {}

    def request_handler(self, req: Request):
        """
        The handler of requests.
        :param req:
        :return:
        """
        req = Request() if req is None else req

        rt = self.e_mgr.create_event(RecvEvent, req, req.path)

        if isinstance(rt, ReturnData):
            return rt
        else:
            return ReturnData(ReturnData.OK, rt)

    def _schedule_activity_list(self):
        """
        Check the online status of users.
        :return:
        """
        # Monitor the activity of users and mark them as offline if they are inactive
        for k, v in list(self.activity_dict.items()):
            self.activity_dict[k] = v - 1
            if v <= 0:
                with self.update_user_data(k) as user:
                    user.status = 'temporarily away'
            elif v <= -180:
                self.activity_dict.pop(k)
                with self.update_user_data(k) as user:
                    user.status = 'offline'
                    user.token = get_random_token(128)

    def _schedule_cleaner(self):
        # Remove expired events from the event database

        del_e_count = 0
        del_sid_count = 0

        for i in self.db_event.find({}):
            if i and time.time() - i['time'] > self.event_timeout:
                self.db_event.delete_one({'_id': i['_id']})
                del_e_count += 1

        for k, v in list(self.event_sid_table.items()):
            try:
                allow_del = self.db_event.find_one({'rid': v}) or time.time() - self.get_user_event(v)[
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

    def _load_auxiliary_events(self):
        """
        Load auxiliary events.
        :return:
        """
        for class_ in self.dol.load_objs_from_group('auxiliary_events'):
            # logout
            logging.debug(_('Auxiliary event "{}" loaded.').format(class_.__name__))

            self.e_mgr.add_auxiliary_event(event=class_)

    def start(self):
        """
        Start the server.
        :return:
        """
        # Load auxiliary events.
        logging.info(_('Loading auxiliary events...'))
        self._load_auxiliary_events()

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
        """
        Start the server and run forever.
        :return:
        """
        self.start()
        while self.running:
            schedule.run_pending()
            time.sleep(0.1)

    def close(self):
        """
        Close the server.
        :return:
        """
        # save data and exit
        self.logger.info(_('Saving data...'))

        self.running = False

        self.logger.info(_('Server closed.'))

    @contextlib.contextmanager
    def update_user_data(self, user_id: str):
        """
        Get the user object.
        :param user_id: The id of user.
        :return:
        """
        with self.db_account.enter_one({'user_id': user_id}) as i:
            user: User = agar(i.data)
            yield user
            i.data = dehydrate(user)

    def new_user(self, user: User):
        self.db_account.insert_one(dehydrate(user))

    def get_user(self, user_id: str) -> User:
        if d := self.db_account.find_one({'user_id': user_id}):
            return agar(d.data)
        else:
            raise KeyError('User not found.')

    def new_group(self, group: Group):
        self.db_group.insert_one(dehydrate(group))

    def get_group(self, group_id: str) -> Group:
        if d := self.db_group.find_one({'id': group_id}):
            return agar(d.data)
        else:
            raise KeyError('Group not found.')

    @contextlib.contextmanager
    def update_group_data(self, group_id: str):
        """
        Get the user object.
        :param group_id: The id of group.
        :return:
        """
        with self.db_group.enter_one({'id': group_id}) as i:
            group: Group = agar(i.data)
            yield group
            i.data = dehydrate(group)

    def is_user_exist(self, user_id: str) -> bool:
        """
        Check if the user exists.
        :param user_id: The id of user.
        :return:
        """
        try:
            self.get_user(user_id)
        except KeyError:
            return False
        else:
            return True

    def get_user_event(self, event_id: str) -> Mapping[str, Any]:
        """
        Get the event data.
        :param event_id:
        :return:
        """
        eid = copy.copy(event_id)

        if eid in self.event_sid_table:
            eid = self.event_sid_table[eid]
        if d := self.db_event.find_one({'rid': eid}):
            return d.data
        else:
            raise KeyError('Event not found.')

    def is_user_event_exist(self, event_id: str) -> bool:
        """
        Check if the event exists.
        :param event_id:
        :return:
        """
        return self.get_user_event(event_id) is not None

    def check_file_exists(self, file_hash: str):
        """
        Check if the file exists.
        :param file_hash:
        :return:
        """
        upl_folder = self.config.get_from_pointer('/network/upload/upload_folder', default='static/files')
        return os.path.exists(os.path.join(upl_folder, file_hash))

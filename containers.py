#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：containers.py

@Author     : hsn

@Date       ：2023/3/1 下午6:30

@Version    : 1.0.0
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
import time
from typing import Any

from RPDB.database import RPDB
from flask import jsonify

import util
from util import get_random_token
from util.jelly import Jelly


class EventContainer:
    def __init__(self, data_base: RPDB):
        # initialize a new event container
        self.data_base = data_base
        # generate a random 8-characters long token as a unique identifier for this event container
        while True:
            rid = get_random_token(8)
            if not self.data_base.exists(rid):
                break
        self.rid = rid
        # create an empty dictionary to store the event data
        self.json = {}
        # initialize the container with the rid and current time
        self.add('rid', self.rid).add('time', time.time())

    def __call__(self, key: str, value: Any) -> None:
        # add a new key-value pair to the event data
        self.json[key] = value

    def write_in(self) -> None:
        # write the event data to the database
        with self.data_base.enter(self.rid) as v:
            v.value = self.json

    def add(self, key: str, value: Any) -> 'EventContainer':
        # add a new key-value pair to the event data and return the container object
        self.json[key] = value
        return self


class ReturnData:
    ERROR = 1
    NULL = 2
    OK = 0

    def __init__(self, status: int = OK, msg: str = ''):
        # initialize a new ReturnData object with a status and message
        status_text = 'ok' if status == self.OK else 'error' if status == self.ERROR else 'null'
        self.json_data = {'status': status_text, 'message': msg}

    def add(self, key: str, value: Any) -> 'ReturnData':
        # add a new key-value pair to the response data and return the object
        self.json_data[key] = value
        return self

    def jsonify(self):
        # convert the response data to a JSON object
        return jsonify(self.json_data)

    def __call__(self) -> dict:
        # return the response data as a dictionary
        return self.json_data


class User(Jelly):
    def __init__(self, user_id: str, password: str, user_name: str):
        super().__init__()
        self.hash_password = None
        self.salt = None
        self.user_id = user_id
        self.user_name = user_name
        self.change_password(password)

    def _var_init(self):
        self.todo_list = []
        self.token = ''
        self.status = 'offline'
        self.friend_dict = {}
        self.groups_dict = {}
        self.email = ''

    def change_password(self, password: str):
        """
        Changes the user's password and generates a new salted hash.
        :param password: The new password to set.
        """
        self.salt = util.get_random_token(16)
        self.hash_password = util.salted_hash(password, self.salt, self.user_id)

    def auth(self, password: str) -> bool:
        """
        Checks if the provided password matches the user's salted hash.
        :param password: The password to check.
        :return: True if the password is correct, False otherwise.
        """
        return util.salted_hash(password, self.salt, self.user_id) == self.hash_password

    def is_in_group(self, server, group_id: str) -> bool:
        """
        Checks if the user is a member of a group.
        :param server: The server object.
        :param group_id: The ID of the group to check.
        :return: True if the user is a member of the group, False otherwise.
        """
        db_group = server.db_group
        if not db_group.exists(group_id):
            return False

        group = db_group.get(group_id)
        if group_id in self.groups_dict and self.user_id in group.member_dict:
            return True

        return False

    def add_user_event(self, ec: EventContainer):
        """
        Adds an event to the user's to-do list.
        :param ec: The event to add.
        """
        self.todo_list.append(ec.json)

    def add_fri_msg2todos(self, server, user_id, name, nick, msg_):
        """
        This function adds a friend message to the event container and writes it in.

        :param user_id: the user id
        :param server: server object
        :param name: name of the friend
        :param nick: nickname of the friend
        :param msg_: the message to be added
        :return: None
        """
        # create a new event container with the server's database event
        ec = EventContainer(server.db_event)

        # add event attributes to the event container
        ec.add('type', 'friend_msg')
        ec.add('rid', ec.rid)
        ec.add('user_id', user_id)  # deprecated
        ec.add('friend_id', user_id)
        ec.add('friend_nick', nick)
        ec.add('friend_name', name)
        ec.add('msg', {"msg_chain": [{"type": "text", "msg": msg_}]} if not isinstance(msg_, dict) else msg_)
        ec.add('_WARNING', 'user_id is deprecated!!!')
        ec.add('time', time.time())

        # write the event container to the database
        ec.write_in()

        # add the event container to the user's event list
        self.add_user_event(ec)

    def auth_token(self, token: str) -> bool:
        """
        Checks if the provided token matches the user's token.
        :param token: The token to check.
        :return: True if the token is correct, False otherwise.
        """
        return self.token == token

    def add_user_to_friend_list(self, user_id, nick):
        if user_id not in self.friend_dict:
            self.friend_dict[user_id] = {'nick': nick, 'time': time.time()}
            return True
        return False


class Group(Jelly):
    # Define permission constants
    PERMISSION_OWNER = 0
    PERMISSION_ADMIN = 1

    def __init__(self, group_id):
        # Call the __init__ method of the superclass
        super().__init__()
        # Initialize the group ID
        self.id = group_id
        # Initialize variables for group name, member dictionary, owner ID,
        # admin list, member settings, and ban dictionary
        self.name = ''
        self.member_dict = {}
        self.owner = ''
        self.admin_list = set()
        self.member_settings = {}
        self.ban_dict = {}
        # Initialize group settings with default values
        '''
                verification_method:
                ac:administrator consent--需要管理同意
                fr:free--自由进出
                aw:answer question--需要回答问题
                na:not allowed--不允许加入
        '''
        self.group_settings = {
            'verification_method': 'ac',
            'question': '',
            'answer': ''
        }

    def broadcast(self, server, user_id: str, ec: EventContainer):
        """
        Send an event to all group members except for the specified user.

        :param server: Server object
        :param user_id: ID of the user who triggered the event
        :param ec: EventContainer object to broadcast
        """
        # Iterate over all members except for the specified user
        for member_id in filter(lambda j: j != user_id, self.member_dict.keys()):
            # Get the User object for the member
            with server.open_user(member_id) as u:
                user: User = u.value
                # Add the event to the user's todo_list
                user.add_user_event(ec)

    def permission_match(self, user_id: str, permission=PERMISSION_ADMIN) -> bool:
        """
        Check if the specified user has the specified permission for the group.

        :param user_id: ID of the user to check
        :param permission: Permission level to check (default is PERMISSION_ADMIN)
        :return: True if the user has the specified permission, False otherwise
        """
        if permission == self.PERMISSION_ADMIN:
            # Check if the user is the group owner or in the admin list
            return user_id == self.owner or user_id in self.admin_list
        elif permission == self.PERMISSION_OWNER:
            # Check if the user is the group owner
            return user_id == self.owner
        else:
            # Invalid permission level
            return False

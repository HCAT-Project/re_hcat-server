#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : containers.py

@Author     : hsn

@Date       : 2023/3/1 下午6:30

@Version    : 1.0.0
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
import time
import uuid
from datetime import timedelta, datetime
from typing import Any
from uuid import uuid1

from flask import jsonify, make_response, Response

import src.util.crypto
import src.util.text
from src.db_adapter.base_dba import BaseCA
from src.util.config_parser import ConfigParser
from src.util.jelly import Jelly


class EventContainer:
    def __init__(self, data_base: BaseCA):
        # initialize a new event container
        self.data_base = data_base
        # generate an uuid for this event container
        self.rid = str(uuid1())
        # create an empty dictionary to store the event data
        self.json = {}
        # initialize the container with the rid and current time
        self.add('rid', self.rid).add('time', time.time())

    def __call__(self, key: str, value: Any) -> None:
        # add a new key-value pair to the event data
        self.json[key] = value

    def write_in(self) -> None:
        # write the event data to the database
        self.data_base.insert_one(self.json)

    def add(self, key: str, value: Any) -> 'EventContainer':
        # add a new key-value pair to the event data and return the container object
        self.json[key] = value
        return self

    def get_sid(self, table: dict) -> str:
        # get a 4 digit random string
        while True:
            sid = src.util.crypto.get_random_token(4).lower()
            if sid not in table:
                break
        table[sid] = self.rid
        return sid


class ReturnData:
    ERROR = 1
    NULL = 2
    OK = 0
    status_text_list = ['ok', 'error', 'null']

    def __init__(self, status: int = OK, msg: str = ''):
        # initialize a new ReturnData object with a status and message
        status_text = self.status_text_list[status]
        self.json_data = {'status': status_text, 'message': msg}

    def add(self, key: str, value: Any) -> 'ReturnData':
        # add a new key-value pair to the response data and return the object
        if key.startswith('_'):
            raise ValueError('key must not start with "_"', key)
        self.json_data[key] = value
        return self

    def set_cookie(self,
                   key: str,
                   value: str = "",
                   max_age: timedelta | int | None = None,
                   expires: str | datetime | int | float | None = None,
                   path: str | None = "/",
                   domain: str | None = None,
                   secure: bool = False,
                   httponly: bool = False,
                   samesite: str | None = None):
        if '_cookies' not in self.json_data:
            self.json_data['_cookies'] = {}
        self.json_data['_cookies'][key] = {'value': value, 'max_age': max_age, 'expires': expires, 'path': path,
                                           'domain': domain, 'secure': secure, 'httponly': httponly,
                                           'samesite': samesite}

    def jsonify(self):
        # convert the response data to a JSON object
        return jsonify(self.json_data)

    def flask_respify(self) -> Response:
        resp = make_response(jsonify(self.json_data), 200)
        if self.json_data.get('_cookies', False):
            for k, v in self.json_data['_cookies'].items():
                resp.set_cookie(key=k, **v)
        return resp

    def __call__(self) -> dict:
        # return the response data as a dictionary
        return self.json_data

    def __str__(self):
        # return the response data as a JSON string
        return str(self.json_data)


class User(Jelly):
    """
    Assuming we need to create a new user in a chat application, we can use the User class to create a new user object and perform various operations on the user, such as changing passwords, adding to-do items, adding friends, joining groups, etc.

    Firstly, we need to instantiate the User class and pass in the user ID, password, and username:

    user = User('jane123', 'password123', 'Jane')

    Then, we can use the add_user_event() method to add an event container to the user's to-do list:

    ec = EventContainer(db_event)
    ec.add('type', 'message')
    ec.add('friend_id', '789012')
    ec.add('msg', 'Hello, how are you?')
    ec.add('time', time.time())
    user.add_user_event(ec)

    Next, we can use the change_password() method to change the user's password:

    user.change_password('newpassword123')

    Then, we can use the auth() method to verify if the user's password is correct:

    if user.auth('newpassword123'):
        print('Password is correct')
    else:
        print('Password is incorrect')

    Finally, we can use the auth_token() method to verify if the user's token is correct:

    if user.auth_token('mytoken'):
        print('Token is correct')
    else:
        print('Token is incorrect')

    In this way, we have successfully created a new user and performed various operations on it, such as adding to-do items, changing passwords, verifying passwords and tokens, adding friends, etc.
    """

    def __init__(self, user_id: str, password: str, user_name: str, password_hash_config: ConfigParser):
        """
        Creates a new user object.
        :param user_id: The ID of the user.
        :param password: The password of the user.
        :param user_name: The name of the user.
        """
        super().__init__()
        self.hash_password: str = str()
        self.salt = None
        self.user_id = user_id
        self.user_name = user_name
        self.change_password(password=password, method=password_hash_config.get('password_hash', 'scrypt'),
                             **password_hash_config['kwargs'])

    def _var_init(self):
        self.todo_list = []
        self.token = ''
        self.status = 'offline'
        self.friend_dict = {}
        self.groups_dict = {}
        self.email = ''
        self.language = 'en_US'
        self.avatar = ''
        self.bio = 'NULL'

    def change_password(self, password: str, method='scrypt', **kwargs):
        """
        Changes the user's password and generates a new salted hash.
        :param method: The method of hashing to use.See https://docs.python.org/zh-cn/3.10/library/hashlib.html.
        :param password: The new password to set.
        """

        self.hash_password = src.util.crypto.password_hash(password=password, method=method, **kwargs)

    def auth(self, password: str) -> bool:
        """
        Checks if the provided password matches the user's salted hash.
        :param password: The password to check.
        :return: True if the password is correct, False otherwise.
        """
        if self.hash_password.find('$') != -1:
            return src.util.crypto.check_password_hash(password=password, hash_=self.hash_password)
        else:
            # sha256 and sha1
            if len(self.hash_password) == 64:
                return src.util.crypto.salted_sha256(password, self.salt, self.user_id) == self.hash_password
            elif len(self.hash_password) == 40:
                return src.util.crypto.salted_sha1(password, self.salt, self.user_id) == self.hash_password
            else:
                return False

    def is_in_contact(self, friend_id: str) -> bool:
        if friend_id in self.friend_dict:
            return True

    def get_friend(self, friend_id) -> dict:
        return self.friend_dict.get(friend_id, default=None)

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
        self.todo_list.append(ec.rid)

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
        """
        This function adds a user to the friend list.
        :param user_id: The user ID to add.
        :param nick: The nickname you want to set.
        :return: If the user is added successfully, return True, otherwise return False.
        """
        # Check if the user is already in the friend list.
        if user_id not in self.friend_dict:
            self.friend_dict[user_id] = {'nick': nick, 'time': time.time()}
            return True
        return False


class Group(Jelly):
    """
    Assuming we want to create a new group in a chat application and add members to it, we can use the Group class to achieve this.

    Firstly, we need to instantiate the Group class and pass in the group ID:

    group = Group('group_123')

    Then, we can add members to the group, as shown below:

    group.add_member(user1)
    group.add_member(user2)
    group.add_member(user3)

    Next, we can set one of the members as the group owner, as shown below:

    group.owner = user1.user_id

    Then, we can set a member as an administrator, as shown below:

    group.admin_list.add(user2.user_id)

    Finally, we can broadcast a message to the group, as shown below:

    ec = EventContainer(db_event)
    ec.add('type', 'message')
    ec.add('sender', 'user_1')
    ec.add('msg', 'Hello, group!')
    ec.add('time', time.time())
    group.broadcast(server, user1.username, ec)

    In this way, we have successfully created a new group, added members to it, set a group owner and administrator, and broadcasted a message to the group.
    """
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

    def broadcast(self, ec: EventContainer, server, *, user_id: str):
        """
        Send an event to all group members except for the specified user.

        :param server: Server object
        :param user_id: ID of the user who triggered the event
        :param ec: EventContainer object to broadcast
        """
        # Iterate over all members except for the specified user
        for member_id in filter(lambda j: j != user_id, self.member_dict.keys()):
            # Get the User object for the member
            with server.update_user_data(member_id) as user:
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


class Request:
    def __init__(self, path: str = '/', form: dict = None, files=None, cookies: dict = None):
        super().__init__()
        if files is None:
            files = {}
        if cookies is None:
            cookies = {}
        if form is None:
            form = {}
        self.id = uuid.uuid4()
        self.cookies = cookies
        self.form = form
        self.path = path
        self.files = files

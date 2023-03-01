#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：register.py

@Author     : hsn

@Date       ：2023/3/1 下午6:26

@Version    : 1.0.0
"""
#  Copyright 2023. hsn
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
from html import escape

from containers import ReturnData, User
from event.base_event import BaseEvent


class Register(BaseEvent):
    auth = False

    def _run(self, user_id, password, username):
        if self.server.is_user_exist(user_id):
            return ReturnData(ReturnData.ERROR, 'ID has been registered.').jsonify()

        # check if user_id is legal
        reg = r'^[a-zA-Z][a-zA-Z0-9_]{4,15}$'
        if not re.match(reg, user_id):
            return ReturnData(ReturnData.ERROR,
                              f'User ID does not match {reg} .').jsonify()

        # check if the password is longer than 6 digits
        if len(password) < 6:
            return ReturnData(ReturnData.ERROR, 'Password is too short.')

        with self.server.open_user(user_id) as u:
            u.value = User(user_id, password, escape(username))
            return ReturnData(ReturnData.OK)

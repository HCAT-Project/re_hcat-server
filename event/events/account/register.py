#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：register.py

@Author     : hsn

@Date       ：2023/3/1 下午6:26

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

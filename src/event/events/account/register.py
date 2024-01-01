#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : register.py

@Author     : hsn

@Date       : 2023/3/1 下午6:26

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
import re

from src.containers import ReturnData, User
from src.event.base_event import BaseEvent
from src.util.config_parser import ConfigParser
from src.util.regex import name_regex


class Register(BaseEvent):
    """
    Register
    Success -> {status: 'ok',msg: 'Successfully registered.'}
    Error -> {status: 'error', message: error message}
    """
    auth = False

    def _run(self, user_id: str, password: str, username: str):
        _ = self.gettext_func
        if self.server.is_user_exist(user_id):
            return ReturnData(ReturnData.ERROR, _('ID has been registered.'))

        # check if user_id is legal

        if not re.match(name_regex, user_id):
            return ReturnData(ReturnData.ERROR,
                              _('User ID does not match {} .').format(name_regex))

        # check if the password is longer than 6 digits
        if len(password) < 6:
            return ReturnData(ReturnData.ERROR, _('Password is too short.'))

        crypto_default = {"crypto": {
            "password": {
                "method": "scrypt",
                "kwargs": {
                    "salt_len": 16,
                    "n": 16384,
                    "r": 8,
                    "p": 1,
                    "maxmem": 0
                }
            }
        }}
        user = User(user_id, password, username,
                    ConfigParser(self.server.config.get_from_pointer('/crypto/password', crypto_default)))
        user.language = self.lang

        user.add_fri_msg2todos(self.server, '0sAccount', _('Account_BOT'), _('Account_BOT'),
                               _('Welcome to HCAT!\\n'
                                 'The first thing you need to do is use `/email bind [email]` to '
                                 'bind your email.\\n'
                                 'Then you can use `/email code [code]` to verify your email.\\n'
                                 'After that, you can use `/email unbind` to unbind your email if you want.\\n'
                                 'Have fun!'))
        self.server.new_user(user)
        return ReturnData(ReturnData.OK, _('Successfully registered.'))

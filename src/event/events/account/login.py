#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : login.py

@Author     : hsn

@Date       : 2023/3/1 下午6:25

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
import json

import src.util.crypto
import src.util.text
from src.containers import ReturnData, User
from src.event.base_event import BaseEvent


class Login(BaseEvent):
    auth = False

    def _run(self, user_id, password):
        _ = self.gettext_func
        if not self.server.is_user_exist(user_id):
            return ReturnData(ReturnData.NULL, _('User does not exist.'))

        self.server.activity_dict[user_id] = 30

        with self.server.update_user_data(user_id) as user:
            if user.auth(password):
                user.status = 'online'
                # generate token
                user.token = src.util.crypto.get_random_token()

                # init a response
                resp = ReturnData(ReturnData.OK)

                # generate auth_data
                auth_data = json.dumps(
                    {'user_id': user_id, 'token': user.token, 'salt': src.util.crypto.get_random_token()})

                # crypto
                aes = src.util.crypto.AesCrypto(self.server.key)

                # set a @Yummy_Cookies_S
                # XD
                if self.server.config['sys']['domain'] is not None:
                    resp.set_cookie('auth_data', aes.encrypt(auth_data), samesite='Strict',
                                    domain=self.server.config['sys']['domain'])
                else:
                    resp.set_cookie('auth_data', aes.encrypt(auth_data), samesite='Strict')

                # check if @0sAccount in friend_list
                user.add_user_to_friend_list('0sAccount', _('Account_BOT'))

                # return
                return resp
            else:
                return ReturnData(ReturnData.ERROR, _('Incorrect user ID or password.'))

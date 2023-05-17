#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : get_user_name.py

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
import importlib

from src.containers import User, ReturnData
from src.event.base_event import BaseEvent


class GetUserName(BaseEvent):
    auth = False

    def _run(self, user_id: str):
        _ = self.gettext_func
        if len(user_id) >= 2:
            if user_id[0] in [str(i) for i in range(10)] and user_id[1] == 's':
                service_id = user_id[2:].rstrip(' ')
                name = importlib.import_module(f'src.event.pri_events.service.{service_id}.__init__').name
                rt = ReturnData(ReturnData.OK).add('data', name).add('nick', name)
                return rt

        # get nick if logged in
        nick = None
        if self.user_id is not None:
            with self.server.open_user(self.user_id) as u:
                user: User = u.value
                if user_id in user.friend_dict:
                    nick = user.friend_dict[user_id]['nick']

        # get username
        if self.server.is_user_exist(user_id):
            with self.server.open_user(user_id) as u:
                user: User = u.value
                rt = ReturnData(ReturnData.OK).add('data', user.user_name)
                if nick is not None:
                    rt.add('nick', nick)
                return rt
        else:
            return ReturnData(ReturnData.NULL, _('User does not exist.')).jsonify()

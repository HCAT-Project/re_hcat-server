#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：get_user_name.py

@Author     : hsn

@Date       ：2023/3/1 下午6:25

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

import importlib

from containers import User, ReturnData
from event.base_event import BaseEvent


class GetUserName(BaseEvent):
    auth = False

    def _run(self, user_id: str):
        if user_id[0] in [str(i) for i in range(10)] and user_id[1] == 's':
            service_id = user_id[2:].rstrip(' ')
            name = importlib.import_module(f'event.pri_events.service.{service_id}.__init__').name
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
            return ReturnData(ReturnData.NULL, 'User does not exist.').jsonify()

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：create_group.py

@Author     : hsn

@Date       ：2023/3/1 下午6:27

@Version    : 1.0.0
"""
#  Copyright 2023. HCAT-Project-Team
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

import time
from html import escape

import util
from containers import Group, User, ReturnData
from event.base_event import BaseEvent


class CreateGroup(BaseEvent):
    auth = True

    def _run(self, group_name):
        group_name_ = escape(group_name)
        while True:
            group_id = '0g' + util.get_random_token(5, upper=False)
            if not self.server.db_group.exists(group_id):
                break
        group = Group(group_id)
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            user.groups_dict[group_id] = {'remark': group_name_, 'time': time.time()}
            user_name = user.user_name

        # set group
        group.name = group_name_
        # todo:create group limit
        group.member_dict[self.user_id] = {'nick': user_name,
                                           'time': time.time()}
        group.owner = self.user_id
        with self.server.db_group.enter(group_id) as g:
            g.value = group
        return ReturnData(ReturnData.OK, '').add('group_id', group_id)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : create_group.py

@Author     : hsn

@Date       : 2023/3/1 下午6:27

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

import src.util.crypto
import src.util.text
from src.containers import Group, ReturnData
from src.event.base_event import BaseEvent


class CreateGroup(BaseEvent):
    """
    Create group
    Success -> {status: 'ok',message: 'Group created.',group_id: group_id}
    Error -> {status: 'error', message: error message}
    """
    auth = True
    returns = {'group_id': str}

    def _run(self, group_name:str):
        group_name_ = group_name
        while True:
            group_id = '0g' + src.util.text.random_str(5, upper=False)
            if not self.server.db_group.find_one(group_id):
                break
        group = Group(group_id)
        with self.server.update_user_data(self.user_id) as user:
            user.groups_dict[group_id] = {'remark': group_name_, 'time': time.time()}
            user_name = user.user_name

        # set group
        group.name = group_name_
        # todo:create group limit
        group.member_dict[self.user_id] = {'nick': user_name,
                                           'time': time.time()}
        group.owner = self.user_id
        self.server.new_group(group)
        return ReturnData(ReturnData.OK, '').add('group_id', group_id)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：change_user_nick.py

@Author     : hsn

@Date       ：2023/3/1 下午6:27

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

from html import escape

from containers import ReturnData, Group
from event.base_event import BaseEvent


class ChangeUserNick(BaseEvent):
    auth = True

    def _run(self, group_id, nick, member_id=None):
        _user_id = self.user_id if member_id is None else member_id

        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if member_id is not None and self.user_id not in list(group.admin_list) + [group.owner]:
                return ReturnData(ReturnData.ERROR, 'You don\'t have permission.')

            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if _user_id not in group.member_dict:
                return ReturnData(ReturnData.ERROR, 'You are not in the group.')

            group.member_dict[_user_id]['nick'] = escape(nick)

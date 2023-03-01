#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：get_setting.py

@Author     : hsn

@Date       ：2023/3/1 下午6:28

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

from containers import User, ReturnData, Group
from event.base_event import BaseEvent


class GetSetting(BaseEvent):
    auth = True

    def _run(self, group_id):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if group_id not in user.groups_dict:
                return ReturnData(ReturnData.NULL, 'You are not in the group.')

        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            return ReturnData(ReturnData.OK).add('data', group.group_settings)

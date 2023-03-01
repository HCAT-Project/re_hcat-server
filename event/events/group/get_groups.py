#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：get_groups.py

@Author     : hsn

@Date       ：2023/3/1 下午6:28

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

from containers import User, ReturnData
from event.base_event import BaseEvent


class GetGroups(BaseEvent):
    auth = True

    def _run(self):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            return ReturnData(ReturnData.OK).add('data',
                                                 {i: {
                                                     'remark': user.groups_dict[i]['remark'],
                                                     'group_name': self.server.db_group.get(i).name,
                                                     'nick': self.server.db_group.get(i).member_dict[self.user_id][
                                                         'nick']

                                                 }
                                                     for i in list(user.groups_dict)})

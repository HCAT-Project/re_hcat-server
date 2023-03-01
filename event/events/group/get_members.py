#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：get_members.py

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

from containers import Group, ReturnData
from event.base_event import BaseEvent


class GetMembers(BaseEvent):
    auth = True

    def _run(self, group_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')
            if self.user_id in group.member_dict:
                return ReturnData(ReturnData.OK).add('data', {
                    k: {
                        'permission':
                            (
                                'member' if (k not in group.admin_list and k != group.owner) else
                                'owner' if k == group.owner else
                                'admin'
                            )
                    }
                    for k in group.member_dict})
            else:
                return ReturnData(ReturnData.NULL, 'You are not in the group.')

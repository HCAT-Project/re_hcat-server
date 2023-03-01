#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：transfer_ownership.py

@Author     : hsn

@Date       ：2023/3/1 下午6:29

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

from containers import Group, ReturnData
from event.base_event import BaseEvent


class TransferOwnership(BaseEvent):
    auth = True

    def _run(self, group_id, member_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id != group.owner:
                return ReturnData(ReturnData.ERROR, 'You are not the owner.')

            if member_id not in group.member_dict:
                return ReturnData(ReturnData.NULL, f'No member with id:"{member_id}"')

            if member_id == self.user_id:
                return ReturnData(ReturnData.ERROR, 'the member is already an owner.')

            group.owner = member_id
            group.admin_list.add(self.user_id)
            return ReturnData(ReturnData.OK)

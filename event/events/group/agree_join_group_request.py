#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：agree_join_group_request.py

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

import time

from containers import User, ReturnData, Group
from event.base_event import BaseEvent


class AgreeJoinGroupRequest(BaseEvent):
    auth = True

    def _run(self, rid):
        if not self.server.db_event.exists(rid):
            return ReturnData(ReturnData.NULL, 'Event does not exist.')

        with self.server.db_event.enter(rid) as e:
            event: dict = e.value
            req_user_id = event['user_id']
            group_id = event['group_id']

        with self.server.open_user(req_user_id) as u:
            user: User = u.value
            req_user_name = user.user_id

        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            group_name = group.name
            if self.user_id not in list(group.admin_list) + [group.owner]:
                return ReturnData(ReturnData.ERROR, 'You don\'t have permission.')
            group.member_dict[req_user_id] = {'nick': req_user_name}

        with self.server.open_user(req_user_id) as u:
            user: User = u.value
            user.groups_dict[group_id] = {'remark': group_name, 'time': time.time()}
            return ReturnData(ReturnData.OK)

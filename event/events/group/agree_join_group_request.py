#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：agree_join_group_request.py

@Author     : hsn

@Date       ：2023/3/1 下午6:27

@Version    : 1.0.0
"""

#  Copyright (C) 2023. HCAT-Project-Team
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
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

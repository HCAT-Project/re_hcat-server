#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：leave.py

@Author     : hsn

@Date       ：2023/3/1 下午6:28

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
from containers import Group, ReturnData
from event.base_event import BaseEvent


class Leave(BaseEvent):
    auth = True

    def _run(self, group_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id not in group.member_dict:
                return ReturnData(ReturnData.NULL, 'You are not in the group.')

            if self.user_id == group_id.owner:
                return ReturnData(ReturnData.ERROR, 'You are the group owner, you can not leave the group.')

            if self.user_id in list(group.admin_list):
                group.admin_list.remove(self.user_id)

            group.member_dict.pop(self.user_id)
            return ReturnData(ReturnData.OK)

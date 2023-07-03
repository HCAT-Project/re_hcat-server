#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : get_name.py

@Author     : hsn

@Date       : 2023/3/1 下午6:28

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
from src.containers import Group, User, ReturnData
from src.event.base_event import BaseEvent


class GetName(BaseEvent):
    auth = False

    def _run(self, group_id):
        _ = self.gettext_func
        if not self.server.db_group.exists(group_id):
            return ReturnData(ReturnData.NULL, _('Group does not exist.'))
        with self.server.update_group_data(group_id) as group:
            group_name = group.name
        remark = group_name

        if self.user_id is not None:
            with self.server.update_user_data(self.user_id) as user:
                if group_id in user.groups_dict:
                    remark = user.groups_dict[group_id]['remark']

        return ReturnData(ReturnData.OK).add('group_name', group_name).add('remark', remark)

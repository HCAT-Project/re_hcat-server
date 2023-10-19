#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : get_groups.py

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
from src.containers import ReturnData
from src.event.base_event import BaseEvent


class GetGroups(BaseEvent):
    auth = True

    def _run(self):
        user = self.server.get_user(self.user_id)
        data = [
            {
                "id": i,
                "group_name": self.server.get_group(i).name,
                "nick": self.server.get_group(i).member_dict[self.user_id]["nick"],
                "remark": user.groups_dict[i]["remark"],
            }
            for i in list(user.groups_dict)
        ]
        return ReturnData(ReturnData.OK).add("data", data)

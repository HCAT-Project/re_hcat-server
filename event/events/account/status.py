#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：status.py

@Author     : hsn

@Date       ：2023/3/1 下午6:26

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
from containers import ReturnData, User
from event.base_event import BaseEvent


class Status(BaseEvent):
    auth = False

    def _run(self, user_id):
        if user_id[0] in [str(i) for i in range(10)] and user_id[1] == 's':
            return ReturnData(ReturnData.OK).add('status', 'online')
        if not self.server.is_user_exist(user_id):
            return ReturnData(ReturnData.NULL, 'User does not exist.')
        with self.server.open_user(user_id) as u:
            user: User = u.value
            return ReturnData(ReturnData.OK).add('status', str(user.status))

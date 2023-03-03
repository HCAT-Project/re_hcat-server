#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：get_todo_list.py

@Author     : hsn

@Date       ：2023/3/1 下午6:25

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
from containers import User, ReturnData
from event.base_event import BaseEvent


class GetTodoList(BaseEvent):
    auth = True

    def _run(self):
        # add activity
        self.server.activity_dict_lock.acquire()
        self.server.activity_dict[self.user_id] = 30
        self.server.activity_dict_lock.release()

        # set status and return the user's todolist
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            user.status = 'online'
            rt = ReturnData(ReturnData.OK).add('data', user.todo_list)
            user.todo_list = []
            return rt

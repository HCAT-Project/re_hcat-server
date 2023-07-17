#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : get_todo_list.py

@Author     : hsn

@Date       : 2023/3/1 下午6:25

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
from src.containers import User, ReturnData
from src.event.base_event import BaseEvent


class GetTodoList(BaseEvent):
    auth = True

    def _run(self):
        # add activity

        self.server.activity_dict[self.user_id] = 30

        # set status and return the user's todolist
        with self.server.update_user_data(self.user_id) as user:
            user.status = 'online'
            rt_todo_list = []
            for i in user.todo_list:
                if (e := self.server.db_event.find_one({'rid': i},masking={'_id':0})) is not None:
                    rt_todo_list.append(e.data)
            rt = ReturnData(ReturnData.OK).add('data', rt_todo_list)
            user.todo_list = []
            return rt

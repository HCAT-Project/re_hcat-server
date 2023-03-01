#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：get_todo_list.py

@Author     : hsn

@Date       ：2023/3/1 下午6:25

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

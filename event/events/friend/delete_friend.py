#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：delete_friend.py

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

from containers import ReturnData, User, EventContainer
from event.base_event import BaseEvent


class DeleteFriend(BaseEvent):
    auth = True

    def _run(self, friend_id):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, 'The person is not your friend.')

            user.friend_dict.pop(friend_id)

        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'friend_deleted'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('time', time.time())
        ec.write_in()

        with self.server.open_user(friend_id) as u:
            user: User = u.value
            user.friend_dict.pop(self.user_id)
            user.add_user_event(ec)
            return ReturnData(ReturnData.OK)

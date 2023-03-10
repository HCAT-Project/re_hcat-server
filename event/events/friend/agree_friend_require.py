#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：agree_friend_require.py

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

from containers import ReturnData, User, EventContainer
from event.base_event import BaseEvent


class AgreeFriendRequire(BaseEvent):
    auth = True

    def _run(self, rid):
        agree_time = time.time()

        with self.server.db_event.enter(rid) as v:
            if v.value is None:
                return ReturnData(ReturnData.NULL, 'This event does not exist.')
            event: dict = v.value

        if event['req_user_id'] != self.user_id:
            return ReturnData(ReturnData.ERROR, 'The person did not send you a friend request.')

        with self.server.open_user(event['user_id']) as u:
            user: User = u.value
            fri_user_name = user.user_name

        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if event['user_id'] in user.friend_dict:
                return ReturnData(ReturnData.ERROR, 'You are already friends with each other.')
            user.friend_dict[event['user_id']] = {'nick': fri_user_name, 'time': agree_time}
            user_name = user.user_name

        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'friend_agree'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('time', time.time())
        ec.write_in()

        with self.server.open_user(event['user_id']) as u:
            user: User = u.value
            user.friend_dict[self.user_id] = {'nick': user_name, 'time': agree_time}
            user.add_user_event(ec)
        return ReturnData(ReturnData.OK)

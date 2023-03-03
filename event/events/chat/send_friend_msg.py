#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：send_friend_msg.py

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
import copy
import time

import util
from containers import User, ReturnData, EventContainer
from event.base_event import BaseEvent


class SendFriendMsg(BaseEvent):
    auth = True

    def _run(self, friend_id, msg):
        # {"msg_chain":[{"type":type,"msg":msg},{"type":type,"msg":msg}]}
        msg_ = copy.copy(msg)
        if len(friend_id) <= 1:
            return ReturnData(ReturnData.NULL, 'The person is not your friend.')

        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, 'The person is not your friend.')

        try:
            msg_ = util.msg_process(msg_)
        except:
            return ReturnData(ReturnData.ERROR, 'Illegal messages.')

        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            name = user.user_name

        with self.server.open_user(friend_id) as u:
            user: User = u.value
            nick = user.friend_dict[self.user_id]['nick']
            ec = EventContainer(self.server.db_event)
            ec. \
                add('type', 'friend_msg'). \
                add('rid', ec.rid). \
                add('user_id', self.user_id). \
                add('friend_id', self.user_id). \
                add('friend_nick', nick). \
                add('friend_name', name). \
                add('msg', msg_). \
                add('_WARNING', 'user_id is deprecated!!!'). \
                add('time', time.time())
            ec.write_in()
            user.add_user_event(ec)
            return ReturnData(ReturnData.OK)

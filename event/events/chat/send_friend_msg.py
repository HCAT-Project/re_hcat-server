#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：send_friend_msg.py

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

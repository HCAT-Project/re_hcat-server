#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：send_group_msg.py

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
from containers import User, ReturnData, EventContainer, Group
from event.base_event import BaseEvent


class SendGroupMsg(BaseEvent):
    auth = True

    def _run(self, group_id, msg):
        msg_ = copy.copy(msg)
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if group_id not in user.groups_dict:
                return ReturnData(ReturnData.NULL, 'You are not in the group.')
            name = user.user_name

        try:
            msg_ = util.msg_process(msg_)
        except:
            return ReturnData(ReturnData.ERROR, 'Illegal messages.')

        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if self.user_id in group.ban_dict:
                if group.ban_dict[self.user_id]['time'] < time.time():
                    del group.ban_dict[self.user_id]
                else:
                    return ReturnData(ReturnData.ERROR, 'You have been banned by admin.')
            nick = group.member_dict[self.user_id]['nick']
            ec = EventContainer(self.server.db_event)
            ec. \
                add('type', 'group_msg'). \
                add('rid', ec.rid). \
                add('user_id', self.user_id). \
                add('group_id', group_id). \
                add('member_nick', nick). \
                add('member_name', name). \
                add('msg', msg_). \
                add('time', time.time())

            group.broadcast(self.server, self.user_id, ec)
            ec.write_in()
        return ReturnData(ReturnData.OK)

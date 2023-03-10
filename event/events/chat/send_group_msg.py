#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：send_group_msg.py

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

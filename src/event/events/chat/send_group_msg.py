#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : send_group_msg.py

@Author     : hsn

@Date       : 2023/3/1 下午6:27

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
import copy
import time

import src.util.text
from src.containers import User, ReturnData, EventContainer, Group
from src.event.base_event import BaseEvent


class SendGroupMsg(BaseEvent):
    auth = True

    def _run(self, group_id, msg):
        _ = self.gettext_func
        msg_ = copy.copy(msg)
        with self.server.update_user_data(self.user_id) as user:
            if group_id not in user.groups_dict:
                return ReturnData(ReturnData.NULL, _('You are not in the group.'))
            name = user.user_name

        try:
            msg_ = src.util.text.msg_process(msg_)
        except ValueError:
            return ReturnData(ReturnData.ERROR, _('Illegal messages.'))

        with self.server.update_group_data(group_id) as group:
            if self.user_id in group.ban_dict:
                if group.ban_dict[self.user_id]['time'] < time.time():
                    del group.ban_dict[self.user_id]
                else:
                    return ReturnData(ReturnData.ERROR, _('You have been banned by admin.'))
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

            group.broadcast(server=self.server, user_id=self.user_id, ec=ec)
            ec.write_in()
        return ReturnData(ReturnData.OK)

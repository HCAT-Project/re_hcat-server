#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : send_friend_msg.py

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
import logging
import time

import src.util.text
from src.containers import ReturnData
from src.event.base_event import BaseEvent


class SendFriendMsg(BaseEvent):
    """
    Send friend message
    Success -> {status: 'ok',rid: rid}
    Error -> {status: 'error', message: error message}
    """
    auth = True
    returns = {'rid': str}

    def _run(self, friend_id: str, msg: str):
        _ = self.gettext_func
        # {"msg_chain":[{"type":type,"msg":msg},{"type":type,"msg":msg}]}
        msg_ = copy.copy(msg)
        if len(friend_id) <= 1:
            return ReturnData(ReturnData.NULL, _('The person is not your friend.'))

        with self.server.update_user_data(self.user_id) as user:
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, _('The person is not your friend.'))

        try:
            msg_ = src.util.text.msg_process(msg_)
        except Exception as err:
            logging.exception(err)
            return ReturnData(ReturnData.ERROR, _('Illegal messages.'))

        with self.server.update_user_data(self.user_id) as user:
            name = user.user_name

        with self.server.update_user_data(friend_id) as user:
            nick = user.friend_dict[self.user_id]['nick']
        ec = self.server.uem.create_event()
        ec. \
            add('type', 'friend_msg'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('friend_id', self.user_id). \
            add('friend_nick', nick). \
            add('friend_name', name). \
            add('receiver', friend_id). \
            add('msg', msg_). \
            add('_WARNING', 'user_id is deprecated!!!'). \
            add('time', time.time())
        ec.write_in()
        self.server.add_event_to_user(friend_id, ec)
        return ReturnData(ReturnData.OK).add('rid', ec.rid)

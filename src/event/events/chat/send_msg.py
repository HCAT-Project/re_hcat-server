#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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
"""
@File       : send_msg.py

@Author     : hsn

@Date       : 2023/3/1 下午6:27

@Version    : 1.0.0
"""

from src.event.base_event import BaseEvent
from src.event.events.chat.send_friend_msg import SendFriendMsg
from src.event.events.chat.send_group_msg import SendGroupMsg


class SendMsg(BaseEvent):
    """
    Send message to friend or group
    Success -> {status: 'ok',rid: rid}
    Error -> {status: 'error', message: error message}
    """
    auth = True
    returns = {'rid': str}

    def _run(self, target_id: str, msg: str):
        if target_id.startswith('0g'):
            e = SendGroupMsg
            self.req.data['group_id'] = target_id
        else:
            e = SendFriendMsg
            self.req.data['friend_id'] = target_id
        return self.server.e_mgr.create_event(e, self.req, self.path)

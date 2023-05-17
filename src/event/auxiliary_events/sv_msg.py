#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : sv_msg.py

@Author     : hsn

@Date       : 2023/3/1 下午6:25

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

from src.event.base_event import BaseEvent
from src.event.events.chat.send_friend_msg import SendFriendMsg
from src.event.pri_events.service.recv_sv_account_msg import RecvSvAccountMsg


class SvMsg(BaseEvent):
    auth = True
    main_event = SendFriendMsg

    def _run(self, friend_id, msg):
        # check if the msg is service Account
        if friend_id[0] in [str(i) for i in range(10)] and friend_id[1] == 's':
            return True, self.e_mgr.create_event(RecvSvAccountMsg, self.req, self.path)

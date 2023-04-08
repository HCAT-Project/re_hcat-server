#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : send_msg.py

@Author     : hsn

@Date       : 2023/3/1 下午6:27

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
from src.event.base_event import BaseEvent
from send_friend_msg import SendFriendMsg
from send_group_msg import SendGroupMsg


class SendMsg(BaseEvent):
    auth = True

    def _run(self, target_id: str, msg):
        if target_id.startswith('0g'):
            return self.e_mgr.create_event(SendGroupMsg, self.req, self.path)
        else:
            return self.e_mgr.create_event(SendFriendMsg, self.req, self.path)

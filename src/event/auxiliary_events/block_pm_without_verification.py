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
@Project : re_hcat-server
@File    : block_pm_without_verification.py
@Date    : 2023/3/3 下午6:27
"""

from src.containers import ReturnData
from src.event.base_event import BaseEvent
from src.event.events.chat.send_friend_msg import SendFriendMsg


class BlockPmWithoutVerification(BaseEvent):
    auth = True
    main_event = SendFriendMsg

    def _run(self, friend_id, msg):

        user = self.server.get_user(self.user_id)

        # check if the msg is service Account
        if friend_id[0] in [str(i) for i in range(10)] and friend_id[1] == 's':
            return False

        elif (user.email is None) and self.server.config.get_from_pointer(
                '/email/enable-email-verification'):
            return True, ReturnData(ReturnData.ERROR, 'Please verify your email first.')

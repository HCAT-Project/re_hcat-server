#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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

"""
@Project : re_hcat-server
@File    : block_pm_without_verification.py
@Date    : 2023/3/3 下午6:27
"""

from src.containers import ReturnData, User
from src.event.base_event import BaseEvent
from src.event.events.chat.send_group_msg import SendGroupMsg


class BlockGmWithoutVerification(BaseEvent):
    auth = True
    main_event = SendGroupMsg

    def _run(self, friend_id, msg):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value

        if (user.email is None) and self.server.config.get_from_pointer('/email/enable-email-verification'):
            return True, ReturnData(ReturnData.ERROR, 'Please verify your email first.')

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : add_friend.py

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
import time

from src.containers import ReturnData
from src.event.base_event import BaseEvent


class AddFriend(BaseEvent):
    """
    Add friend
    Success -> {status: 'ok',message: 'Request sent successfully.'}
    Error -> {status: 'error', message: error message}
    """
    auth = True

    def _run(self, user_id: str, add_info: str = ''):
        _ = self.gettext_func
        if not self.server.is_user_exist(user_id):
            return ReturnData(ReturnData.NULL, _('User does not exist.'))

        if user_id == self.user_id:
            return ReturnData(ReturnData.ERROR, _('You cannot add yourself as a friend.'))

        with self.server.update_user_data(self.user_id) as user:
            if user_id in user.friend_dict:
                return ReturnData(ReturnData.ERROR, _('You are already friends with each other.'))

        ec = self.server.uem.create_event()
        ec. \
            add('type', 'friend_request'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('req_user_id', user_id). \
            add('add_info', add_info). \
            add('time', time.time())
        ec.write_in()

        with self.server.update_user_data(user_id) as user:

            user.add_user_event(ec)
            return ReturnData(ReturnData.OK, _('Request sent successfully.'))

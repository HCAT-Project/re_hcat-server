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
@File       : get_profile.py

@Author     : hsn

@Date       : 7/4/23 8:41 PM

@Version    : 1.0.0
"""
from src.containers import ReturnData
from src.event.base_event import BaseEvent


class GetProfile(BaseEvent):
    auth = False

    def _run(self, user_id):
        _ = self.gettext_func
        # get user data
        user = self.server.get_user(user_id)
        rt = {
            'avatar': user.avatar,
            'name': user.user_name,
            'id': user.user_id,
            'bio': user.bio,
            'status': user.status,
            'gender': user.gender
        }
        if self.user_id is not None:
            is_fri = self.server.get_user(self.user_id).is_in_contact(user_id)
            rt['is_friend'] = is_fri
            if is_fri:
                rt['nick'] = self.server.get_user(self.user_id).get_friend(user_id)['nick']
                rt['time'] = self.server.get_user(self.user_id).get_friend(user_id)['time']
        return ReturnData(ReturnData.OK).add('data', rt)

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
    auth = True

    def _run(self, user_id):
        _ = self.gettext_func
        # get user data
        user = self.server.get_user(user_id)
        rt = ReturnData(ReturnData.OK) \
            .add('avatar', user.avatar) \
            .add('name', user.user_name) \
            .add('id', user.user_id) \
            .add('bio', user.bio)

        if self.user_id is not None:
            rt.add('is_friend', is_fri := self.server.get_user(self.user_id).is_friend(user_id))
            if is_fri:
                rt.add('nick', self.server.get_user(self.user_id).get_friend(user_id)['nick'])
                rt.add('time', self.server.get_user(self.user_id).get_friend(user_id)['time'])

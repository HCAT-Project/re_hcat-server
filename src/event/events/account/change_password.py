#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : change_password.py

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
from src.containers import ReturnData, User
from src.event.base_event import BaseEvent
from src.util.jelly import agar


class ChangePassword(BaseEvent):
    auth = True

    def _run(self, password):
        _ = self.gettext_func
        # check if the password is longer than 6 digits
        if len(password) < 6:
            return ReturnData(ReturnData.ERROR, _('Password is too short.'))
        # get user and change password
        with self.server.update_user_data(self.user_id) as user:
            user.change_password(password)
            return ReturnData(ReturnData.OK)

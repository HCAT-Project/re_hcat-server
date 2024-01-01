#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : change_user_nick.py

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


from src.containers import ReturnData
from src.event.base_event import BaseEvent


class ChangeUserNick(BaseEvent):
    """
    Change user nick
    Success -> {status: 'ok',message: 'Nick changed.'}
    Error -> {status: 'error', message: error message}
    """
    auth = True

    def _run(self, group_id:str, nick:str, member_id:str|None=None):
        _ = self.gettext_func
        _user_id = self.user_id if member_id is None else member_id

        with self.server.update_group_data(group_id) as group:
            if member_id is not None and self.user_id not in list(group.admin_list) + [group.owner]:
                return ReturnData(ReturnData.ERROR, _('You don\'t have permission.'))

            if group is None:
                return ReturnData(ReturnData.NULL, _('Group does not exist.'))

            if _user_id not in group.member_dict:
                return ReturnData(ReturnData.ERROR, _('You are not in the group.'))

            group.member_dict[_user_id]['nick'] = nick
            return ReturnData(ReturnData.OK, _('Nick changed.'))

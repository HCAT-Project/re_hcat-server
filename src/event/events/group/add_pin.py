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
@File       : add_pin.py

@Author     : hsn

@Date       : 8/7/23 9:02 PM

@Version    : 1.0.0
"""
from src.containers import Group, ReturnData
from src.event.base_event import BaseEvent


class AddPin(BaseEvent):
    """
    Add pin
    Success -> {status: 'ok', message: 'Pin added.'}
    Error -> {status: 'error', message: 'You are not an admin.'}
    """
    auth = True

    def _run(self, group_id:str, rid:str):
        _ = self.gettext_func
        with self.server.update_group_data(group_id) as group:
            if group.permission_match(self.user_id, Group.PERMISSION_ADMIN):
                group.pin_list.add(rid)
                return ReturnData(ReturnData.OK, _('Pin added.'))
            else:
                return ReturnData(ReturnData.ERROR, _('You are not an admin.'))

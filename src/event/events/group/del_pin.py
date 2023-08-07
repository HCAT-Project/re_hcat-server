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
@File       : del_pin.py

@Author     : hsn

@Date       : 8/7/23 9:09 PM

@Version    : 1.0.0
"""
from src.containers import Group, ReturnData
from src.event.base_event import BaseEvent


class DelPin(BaseEvent):
    auth = True

    def _run(self, group_id, rid):
        _ = self.gettext_func
        with self.server.update_group_data(group_id) as group:
            if group.permission_match(self.user_id, Group.PERMISSION_ADMIN):
                if rid in group.pin_list:
                    group.pin_list.remove(rid)
                    return ReturnData(ReturnData.OK, _('Pin removed.'))
                else:
                    return ReturnData(ReturnData.ERROR, _('Pin not found.'))
            else:
                return ReturnData(ReturnData.ERROR, _('You are not an admin.'))

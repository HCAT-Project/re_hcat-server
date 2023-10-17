#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : ban.py

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

from src.containers import ReturnData, UserEvent
from src.event.base_event import BaseEvent


class Ban(BaseEvent):
    auth = True

    def _run(self, group_id, member_id, ban_time):
        _ = self.gettext_func
        with self.server.update_group_data(group_id) as group:
            if group is None:
                return ReturnData(ReturnData.NULL, _('Group does not exist.'))

            if (
                    self.user_id not in list(group.admin_list) + [group.owner]) or (
                    member_id in group.admin_list and self.user_id != group.owner) or (
                    member_id == group.owner
            ):
                return ReturnData(ReturnData.ERROR, _('You don\'t have permission.'))

            try:
                group.ban_dict[member_id] = {'time': time.time() + float(ban_time)}
            except TypeError:
                return ReturnData(ReturnData.ERROR, _('Wrong data type.'))

            ec = self.server.uem.create_event()
            ec. \
                add('type', 'banned'). \
                add('rid', ec.rid). \
                add('group_id', group_id). \
                add('time', time.time()). \
                add('ban_time', ban_time)  # second
            ec.write_in()

        with self.server.update_user_data(member_id) as user:
            user.add_user_event(ec)

        return ReturnData(ReturnData.OK, '')

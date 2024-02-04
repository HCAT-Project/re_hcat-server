#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : remove_admin.py

@Author     : hsn

@Date       : 2023/3/1 下午6:29

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


class RemoveAdmin(BaseEvent):
    """
    Remove admin
    Success -> {status: 'ok', message: message}
    """
    auth = True

    def _run(self, group_id:str, admin_id:str):
        _ = self.gettext_func
        with self.server.update_group_data(group_id) as group:
            if group is None:
                return ReturnData(ReturnData.NULL, _('Group does not exist.'))

            if admin_id not in group.admin_list:
                return ReturnData(ReturnData.NULL, _('No admin with id:"{}"').format(admin_id))

            if self.user_id != group.owner:
                return ReturnData(ReturnData.ERROR, _('You are not the owner.'))

            if admin_id == group.owner:
                return ReturnData(ReturnData.ERROR, _('You can\'t make the group owner the admin.'))

            group.admin_list.remove(admin_id)
        ec = self.server.uem.create_event()
        ec. \
            add('type', 'admin_removed'). \
            add('rid', ec.rid). \
            add('group_id', group_id). \
            add('time', time.time()). \
            add('admin_id', admin_id)
        ec.write_in()

        for m in group.member_dict:
            self.server.add_event_to_user(m, ec)
        return ReturnData(ReturnData.OK, _('Admin removed.'))

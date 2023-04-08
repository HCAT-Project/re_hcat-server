#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : kick.py

@Author     : hsn

@Date       : 2023/3/1 下午6:28

@Version    : 1.0.0
"""

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
import time

from src.containers import Group, ReturnData, User, EventContainer
from src.event.base_event import BaseEvent


class Kick(BaseEvent):
    auth = True

    def _run(self, group_id, member_id):
        _ = self.gettext_func
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if self.user_id == member_id:
                return ReturnData(ReturnData.ERROR, _('Can\'t kick yourself out.'))
            if group is None:
                return ReturnData(ReturnData.NULL, _('Group does not exist.'))

            if self.user_id not in list(group.admin_list) + [group.owner]:
                return ReturnData(ReturnData.ERROR, _('You are not the owner.'))

            if member_id not in group.member_dict:
                return ReturnData(ReturnData.NULL, _('No member with id:"{}"').format(member_id))

            if member_id in list(group.admin_list):
                group.admin_list.remove(member_id)

            group.member_dict.pop(member_id)
            ec = EventContainer(self.server.db_event)
            ec. \
                add('type', 'member_removed'). \
                add('rid', ec.rid). \
                add('group_id', group_id). \
                add('time', time.time()). \
                add('member_id', member_id)
            ec.write_in()
            group.broadcast(self.server, '', ec)

        with self.server.open_user(member_id) as u:
            user: User = u.value
            user.groups_dict.pop(group_id)

        return ReturnData(ReturnData.OK)

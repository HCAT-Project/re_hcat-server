#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : transfer_ownership.py

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
from src.containers import ReturnData, UserEvent
from src.event.base_event import BaseEvent


class TransferOwnership(BaseEvent):
    auth = True

    def _run(self, group_id, member_id):
        _ = self.gettext_func
        with self.server.update_group_data(group_id) as group:
            if group is None:
                return ReturnData(ReturnData.NULL, _('Group does not exist.'))

            if self.user_id != group.owner:
                return ReturnData(ReturnData.ERROR, _('You are not the owner.'))

            if member_id not in group.member_dict:
                return ReturnData(ReturnData.NULL, _('No member with id:"{}"').format(member_id))

            if member_id == self.user_id:
                return ReturnData(ReturnData.ERROR, _('the member is already an owner.'))

            group.owner = member_id
            group.admin_list.add(self.user_id)
            ec = self.server.uem.create_event() \
                .add('type', 'group_transfer_ownership') \
                .add('group_id', group_id) \
                .add('member_id', member_id) \
                .add('operator_id', self.user_id)
            ec.write_in()
            group.broadcast(ec=ec, server=self.server,user_id=self.user_id)
            return ReturnData(ReturnData.OK)

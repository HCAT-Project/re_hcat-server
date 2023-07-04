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
@File       : recall.py

@Author     : hsn

@Date       : 7/4/23 9:52 PM

@Version    : 1.0.0
"""
from src.containers import ReturnData, User, EventContainer
from src.db_adapter.base_dba import BaseCA
from src.event.base_event import BaseEvent


class Recall(BaseEvent):
    auth = True

    def _run(self, rid):
        _ = self.gettext_func
        db: BaseCA = self.server.db_event
        if (
                fe := db.find_one({'friend_id': self.user_id, 'rid': rid})
        ) or (
                de := db.find_one({'user_id': self.user_id, 'rid': rid})
        ):
            db.delete_one({'rid': rid})

        else:
            return ReturnData(ReturnData.NULL, _('No such message'))

        if fe:
            with self.server.update_user_data(fe['receiver']) as user:
                user: User
                if rid in user.todo_list:
                    user.todo_list.remove(rid)
                else:
                    ec = EventContainer(self.server.db_event).add('type', 'recall').add('rid', rid)
                    user.todo_list.append(ec)
        else:
            group = self.server.get_group(de['group_id'])

            for i in group.member_dict:
                with self.server.update_user_data(i) as user:
                    user: User
                    if rid in user.todo_list:
                        user.todo_list.remove(rid)
                    else:
                        ec = EventContainer(self.server.db_event).add('type', 'recall').add('rid', rid)
                        user.todo_list.append(ec)
        return ReturnData(ReturnData.OK)

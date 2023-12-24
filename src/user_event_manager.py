#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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

"""
@File       : user_event_manager.py

@Author     : hsn

@Date       : 10/17/23 9:34 PM
"""
from functools import partial

from src.containers import UserEvent
from src.db_adapter.base_dba import BaseCA, Item
from util.text import random_str


class UserEventManager:
    def __init__(self, database: BaseCA):
        self.db = database
        self.sid_table = {}

    def create_event(self) -> UserEvent:
        ue = UserEvent()
        ue.write_in = partial(self.write_in, ue)
        ue.get_sid = partial(self.get_sid, ue)
        return ue

    def get_sid(self, event: UserEvent) -> str:
        while True:
            sid = random_str(4).lower()
            if sid not in self.sid_table:
                break
        self.sid_table[sid] = event.rid
        return sid

    def write_in(self, event: UserEvent):
        self.db.insert_one(event.json)

    def get_event(self, rid: str):

        if rid in self.sid_table:
            rid_ = self.sid_table[rid]
        else:
            rid_ = rid

        if (e := self.db.find_one({'rid': rid_})) is not None:
            e: Item
            return e.data
        else:
            raise KeyError(f'rid {rid} not found')

    def is_event_exist(self, rid: str):
        try:
            self.get_event(rid)
            return True
        except ValueError:
            return False

    def delete(self, rid: str):
        if rid in self.sid_table:
            rid_ = self.sid_table[rid]
            del self.sid_table[rid]
        else:
            rid_ = rid
        self.db.delete_one(rid_)

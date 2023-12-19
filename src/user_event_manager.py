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


class UserEventManager:
    def __init__(self, database: BaseCA):
        self.db = database

    def create_event(self) -> UserEvent:
        ue = UserEvent()
        ue.write_in = partial(self.write_in, ue)
        return ue

    def write_in(self, event: UserEvent):
        self.db.insert_one(event.json)

    def get_event(self, rid):
        if e := self.db.find_one({'rid': rid}) is not None:
            e: Item
            return e.data
        else:
            raise ValueError(f'rid {rid} not found')

    def is_event_exist(self, rid):
        try:
            self.get_event(rid)
            return True
        except ValueError:
            return False

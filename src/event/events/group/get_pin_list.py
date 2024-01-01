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
@File       : get_pin_list.py

@Author     : hsn

@Date       : 8/7/23 9:10 PM

@Version    : 1.0.0
"""
from src.containers import ReturnData, Group
from src.event.base_event import BaseEvent


class GetPinList(BaseEvent):
    """
    Get pin list
    Success -> {status: 'ok', data: [event, ...]}
    Error -> {status: 'error', message: error message}
    """
    auth = True
    returns = {'data': list}
    def _run(self, group_id:str):
        _ = self.gettext_func

        def get_pin_list(group_: Group):
            for i in group_.pin_list:
                if (e := self.server.db_event.find_one({'rid': i}, masking={'_id': 0})) is not None:
                    yield e.data

        group = self.server.get_group(group_id)
        return ReturnData(ReturnData.OK).add('data', list(get_pin_list(group)))

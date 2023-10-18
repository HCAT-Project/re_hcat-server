#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : recv_event.py

@Author     : hsn

@Date       : 2023/3/1 下午6:30

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
import logging

from src.containers import ReturnData
from src.event.base_event import BaseEvent


class RecvEvent(BaseEvent):
    auth = False

    def _run(self):
        event_class = self.server.dol.load_obj_from_group(path=self.path, group='req_events')

        if event_class is None:
            return ReturnData(ReturnData.NULL, 'No Found.')

        try:
            return self.server.e_mgr.create_event(event_class, self.req, self.path)

        except Exception as err:
            logging.exception(err)
            return ReturnData(ReturnData.NULL, 'Internal Server Error.')

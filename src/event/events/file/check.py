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
@File       : check.py

@Author     : hsn

@Date       : 4/9/23 8:25 AM

@Version    : 1.0.0
"""
from src.containers import ReturnData
from src.event.base_event import BaseEvent


class CheckFileExist(BaseEvent):
    auth = False

    def _run(self, sha1):
        return ReturnData(ReturnData.OK if self.server.check_file_exists(sha1) else ReturnData.NULL)

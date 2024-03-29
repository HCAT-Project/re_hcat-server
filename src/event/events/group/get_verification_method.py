#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : get_verification_method.py

@Author     : hsn

@Date       : 2023/3/1 下午6:28

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
from src.containers import ReturnData, Group
from src.event.base_event import BaseEvent


class GetVerificationMethod(BaseEvent):
    auth = True

    def _run(self, group_id):
        _ = self.gettext_func
        try:
            self.server.get_group(group_id)
        except KeyError:
            return ReturnData(ReturnData.NULL, _('Group does not exist.'))

        group: Group = self.server.get_group(group_id)
        return ReturnData(ReturnData.OK). \
            add('data',
                {'verification_method': group.group_settings['verification_method'],
                 'question': group.group_settings['question']})

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : change_group_setting.py

@Author     : hsn

@Date       : 2023/3/1 下午6:27

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
import json

from src.containers import ReturnData
from src.event.base_event import BaseEvent


class ChangeGroupSetting(BaseEvent):
    auth = True

    def _run(self, group_id, setting):
        _ = self.gettext_func
        with self.server.update_group_data(group_id) as group:
            if group is None:
                return ReturnData(ReturnData.NULL, _('Group does not exist.'))

            if self.user_id not in list(group.admin_list) + [group.owner]:
                return ReturnData(ReturnData.ERROR, _('You don\'t have permission.'))
            try:
                setting_ = setting if type(setting) == dict else json.loads(setting)
            except json.JSONDecodeError:
                return ReturnData(ReturnData.ERROR, _('Illegal setting.'))

            error_list = list(filter(lambda x: x not in group.group_settings, setting_))

            if len(error_list) >= 1:
                return ReturnData(ReturnData.NULL, _('key:"{}" does not exist').format(str(error_list)))
            group.group_settings = {k: (setting_[k] if k in setting_ else group.group_settings[k]) for k in
                                    group.group_settings}
            return ReturnData(ReturnData.OK)

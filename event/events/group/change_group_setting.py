#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：change_group_setting.py

@Author     : hsn

@Date       ：2023/3/1 下午6:27

@Version    : 1.0.0
"""
#  Copyright 2023. HCAT-Project-Team
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json

from containers import Group, ReturnData
from event.base_event import BaseEvent


class ChangeGroupSetting(BaseEvent):
    auth = True

    def _run(self, group_id, setting):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id not in list(group.admin_list) + [group.owner]:
                return ReturnData(ReturnData.ERROR, 'You don\'t have permission.')
            try:
                setting_ = setting if type(setting) == dict else json.loads(setting)
            except:
                return ReturnData(ReturnData.ERROR, 'Illegal setting.')

            error_list = list(filter(lambda x: x not in group.group_settings, setting_))

            if len(error_list) >= 1:
                return ReturnData(ReturnData.NULL, f'key:"{str(error_list)}" does not exist')
            group.group_settings = {k: (setting_[k] if k in setting_ else group.group_settings[k]) for k in
                                    group.group_settings}
            return ReturnData(ReturnData.OK)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：get_verification_method.py

@Author     : hsn

@Date       ：2023/3/1 下午6:28

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

from containers import ReturnData, Group
from event.base_event import BaseEvent


class GetVerificationMethod(BaseEvent):
    auth = True

    def _run(self, group_id):
        if not self.server.db_group.exists(group_id):
            return ReturnData(ReturnData.NULL, 'Group does not exist.')
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            return ReturnData(ReturnData.OK). \
                add('data',
                    {'verification_method': group.group_settings['verification_method'],
                     'question': group.group_settings['question']})

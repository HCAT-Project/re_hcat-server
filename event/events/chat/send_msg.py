#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：send_msg.py

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

from event.base_event import BaseEvent
from send_friend_msg import SendFriendMsg
from send_group_msg import SendGroupMsg


class SendMsg(BaseEvent):
    auth = True

    def _run(self, target_id: str, msg):
        if target_id.startswith('0g'):
            return self.e_mgr.create_event(SendGroupMsg, self.req, self.path)
        else:
            return self.e_mgr.create_event(SendFriendMsg, self.req, self.path)

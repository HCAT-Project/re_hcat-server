#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：sv_msg.py

@Author     : hsn

@Date       ：2023/3/1 下午6:25

@Version    : 1.0.0
"""
#  Copyright 2023. hsn
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

import copy

from event.base_event import BaseEvent
from event.events.chat.send_friend_msg import SendFriendMsg
from event.pri_events.service.recv_sv_account_msg import RecvSvAccountMsg


class SvMsg(BaseEvent):
    auth = True
    main_event = SendFriendMsg

    def _run(self, friend_id, msg):
        msg_ = copy.copy(msg)
        # check if the msg is service Account
        if friend_id[0] in [str(i) for i in range(10)] and friend_id[1] == 's':
            return True, self.e_mgr.create_event(RecvSvAccountMsg, self.req, self.path)

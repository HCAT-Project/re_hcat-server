#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：recv_msg.py

@Author     : hsn

@Date       ：2023/3/1 下午6:29

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

from containers import User, ReturnData
from event.base_event import BaseEvent
from util.command_parser import Command


class RecvMsg(BaseEvent):
    auth = True

    def _run(self, msg: str):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            try:

                cmd = Command(json.loads(msg)['msg_chain'][0]['msg'])

                if cmd[0] == 'help':
                    user.add_fri_msg2todos(self.server, '0sAccount', 'Account_BOT', 'Account_BOT',
                                           """
                                           Commands:
                                           /help: this msg.
                                           """)
                else:
                    user.add_fri_msg2todos(self.server, '0sAccount', 'Account_BOT', 'Account_BOT',
                                           "Sorry,i can't understand.")
            except:

                user.add_fri_msg2todos(self.server, '0sAccount', 'Account_BOT', 'Account_BOT',
                                       'Hello, please use `/help` for help.')
            return ReturnData(ReturnData.OK)

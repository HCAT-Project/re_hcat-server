#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：base_event.py

@Author     : hsn

@Date       ：2023/3/1 下午6:29

@Version    : 1.0.0
"""

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
import inspect
import json

import util
from containers import ReturnData, User
from event.event_manager import EventManager
from util.command_parser import Command


class BaseEvent:
    auth = True

    def __init__(self, server, req, path: str, e_mgr: EventManager, user_id=None):
        self.req = req
        self.server = server
        self.path = path
        self.e_mgr = e_mgr
        self.user_id = user_id

    def run(self):

        # get req_data
        req_data = util.request_parse(self.req)

        # get the parameters of the function
        params = inspect.signature(self._run).parameters
        requirements = [i for i in params]
        m_requirements = list(filter(lambda x: str(params[x].default) == '<class \'inspect._empty\'>', requirements))

        # check if the parameters meet the requirements
        if util.ins(m_requirements, req_data):
            if len(requirements) > 0:
                return self._run(*[req_data[k] for k in requirements])
            else:
                return self._run()
        else:
            req_str = ",".join(filter(lambda x: x not in req_data, m_requirements))
            return ReturnData(ReturnData.ERROR,
                              f'Parameters do not meet the requirements:[{req_str}]')

    def _run(self, *args):
        ...


class BaseEventOfSVACRecvMsg(BaseEvent):
    bot_id = None
    bot_name = None

    def __init__(self, *args):
        super().__init__(*args)
        self.cmds = {}

        @util.decorators_with_parameters
        def cmd(func, head):
            self.cmds[head] = func
            return func

        self.cmd = cmd

        @cmd(head='help')
        def help_(cmd):
            self.send_msg("""
            Commands:
            /help
            """ + '\n/'.join(self.cmds.keys()))

        self._reg_cmds()

    def send_msg(self, msg: str):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            user.add_fri_msg2todos(self.server, self.bot_id, self.bot_name, self.bot_name,
                                   msg)

    def _run(self, msg: str):

        try:

            cmd = Command(json.loads(msg)['msg_chain'][0]['msg'])

            if cmd[0] in self.cmds:
                return self.cmds[cmd[0]](cmd[1:])
            else:
                self.send_msg("Sorry,i can't understand.")
        except:
            self.send_msg('Hello, please use `/help` for help.')
        return ReturnData(ReturnData.OK)

    def _reg_cmds(self):
        ...

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

import util
from containers import ReturnData
from event.event_manager import EventManager


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

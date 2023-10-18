#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : event_manager.py

@Author     : hsn

@Date       : 2023/3/1 下午6:24

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
import logging
import time
from typing import Union, Any

import jwt

from src.containers import ReturnData, Request
from src.event.base_event import BaseEventOfAuxiliary, BaseEvent

from src.util.config_parser import ConfigParser
from src.util.crypto import AesCrypto, JWT


class EventManager:

    def __init__(self, server):
        self.server = server
        self.logger = logging.getLogger(__name__)
        self.auxiliary_events = {}

    def add_auxiliary_event(self, event: BaseEventOfAuxiliary, *, main_event: BaseEvent = None):
        if main_event is None:
            if isinstance(event.main_event, (list, tuple)):
                for i in event.main_event:
                    self.add_auxiliary_event(event, main_event=i)
            else:
                self.add_auxiliary_event(event, main_event=event.main_event)

        if main_event not in self.auxiliary_events:
            self.auxiliary_events[main_event] = []
        if event.__dict__.get('priority') is None:
            event.priority = 1000
        self.auxiliary_events[main_event].append({'evt': event, 'priority': event.priority})

    def create_event(self, event, req: Request, path: str):
        assert isinstance(self.server.config, ConfigParser)

        cancel, rd_of_aux_evt = self._run_aux_events(event, path, req)

        # set the default value of variables
        auth_success = False
        auth_data_json = {'user_id': None}

        # check if the 'token' is in `req.cookies`
        if 'token' in req.form:

            # get auth data
            token = req.form['token']
            try:
                # decode the token
                auth_data_json: dict[str, Any] = JWT(self.server.key).decode(token)
                auth_success = True

            except KeyError as err:
                auth_success = False
            except Exception as err:
                self.logger.exception(err)
                auth_success = False

        # check if the auth is successful
        if auth_success or (not event.auth):

            # set the default value of `rt`
            rt = None

            # check if the event is canceled
            if not cancel:
                # run the code of event
                e = event(self.server, req, path, auth_data_json['user_id'])
                rt = e.run()
            f_rt = rt if rt else rd_of_aux_evt
            if auth_success:
                exp = auth_data_json['exp']
                if exp - time.time() < 120:
                    token = JWT(self.server.key).encode(
                        {'user_id': auth_data_json['user_id']}, timeout=600)
                    f_rt.add('token', token)
            return f_rt
        else:
            return ReturnData(ReturnData.ERROR, 'Invalid token.')

    def _run_aux_events(self, event, path, req):
        # run auxiliary events
        rd_of_aux_evt = None
        cancel = False
        # get aux event
        aux_events: dict = self.auxiliary_events.get(event, [])
        aux_e_sorted = map(lambda x: x['evt'], sorted(aux_events, key=lambda x: x['priority']))
        for e in aux_e_sorted:

            # get the return value
            aux_evt_rt_tuple = self.create_event(e, req, path)

            # check if the return value is None
            # if not None set `rd_of_aux_evt` and `cancel` according to the return value
            if aux_evt_rt_tuple is None:
                continue

            aux_evt_rt_tuple = _auto_complete(aux_evt_rt_tuple)

            # set the `rd_of_aux_evt` according to the return value if the return value is not NULL.
            if aux_evt_rt_tuple[1] is not None:
                rd_of_aux_evt = aux_evt_rt_tuple[1]

            # set the cancel
            cancel = aux_evt_rt_tuple[0] or cancel
        return cancel, rd_of_aux_evt


def _auto_complete(ae_rt_temp: Union[bool, ReturnData, tuple]):
    # check if the return value is single value
    if not isinstance(ae_rt_temp, tuple) or len(ae_rt_temp) == 1:
        # set return value to NULL if the value instance is bool
        # else set the bool to False
        return (ae_rt_temp, None) if isinstance(ae_rt_temp, bool) else (False, ae_rt_temp)
    return ae_rt_temp

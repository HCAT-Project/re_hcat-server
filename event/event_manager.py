#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：event_manager.py

@Author     : hsn

@Date       ：2023/3/1 下午6:24

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
import json
import logging

from containers import ReturnData, User
from util import AesCrypto


class EventManager:
    def __init__(self, server):
        self.server = server
        self.logger = logging.getLogger(__name__)
        self.auxiliary_events = {}

    def add_auxiliary_event(self, main_event: type, event: type):
        if main_event not in self.auxiliary_events:
            self.auxiliary_events[main_event] = []
        self.auxiliary_events[main_event].append(event)

    def create_event(self, event, req, path):
        # run auxiliary events
        ae_rt = None
        cancel = False

        # get aux event
        for e in self.auxiliary_events.get(event, []):

            # get the return value
            ae_rt_temp = self.create_event(e, req, path)

            # check if the return value is None
            # if not None set `ae_rt` and `cancel` according to the return value
            if ae_rt_temp is not None:

                # check if the return value is single value
                if not isinstance(ae_rt_temp, tuple) or len(ae_rt_temp) == 1:

                    # set return value to NULL if the value instance is bool
                    # else set the bool to False
                    if isinstance(ae_rt_temp, bool):
                        ae_rt_temp = (ae_rt_temp, ReturnData(ReturnData.NULL, ''))
                    else:
                        ae_rt_temp = (False, ae_rt_temp)

                # set the `ae_rt` according to the return value if the return value is not NULL.
                if ae_rt_temp[1] != ReturnData(ReturnData.NULL, ''):
                    ae_rt = ae_rt_temp[1]

                # set the cancel
                cancel = ae_rt_temp[0] or cancel
        # set the default value of variables
        auth_success = False
        auth_data_json = {'user_id': None}

        # check if the 'auth_data' is in `req.cookies`
        if 'auth_data' in req.cookies:

            # get auth data
            auth_data = req.cookies['auth_data']

            try:
                # decrypt the auth data
                auth_data_decrypto = AesCrypto(self.server.key).decrypt(auth_data)

                # parse the auth data
                auth_data_json = json.loads(auth_data_decrypto)

                # auth the token
                with self.server.open_user(auth_data_json['user_id']) as v:
                    user: User = v.value
                    auth_success = user.auth_token(auth_data_json['token'])
            except:
                if event.auth:
                    return ReturnData(ReturnData.ERROR, 'Invalid token.').jsonify()

        # check if the auth is successful
        if auth_success or not event.auth:

            # set the default value of `rt`
            rt = None

            # check if the event is canceled
            if not cancel:
                # run the code of event
                e = event(self.server, req, path, self, auth_data_json['user_id'])
                rt = e.run()

            # set `ae_rt` to NULL if the `ae_rt` is not existed
            ae_rt = ae_rt if ae_rt is not None else ReturnData(ReturnData.NULL, '')
            print(ae_rt, rt)
            # set `rt` to `ae_rt` if the `rt` is not existed
            rt = rt if rt is not None else ae_rt

            return rt
        else:
            return ReturnData(ReturnData.ERROR, 'Invalid token.').jsonify()

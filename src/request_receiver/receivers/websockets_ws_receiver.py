#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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

"""
@File       : websockets_ws_receiver.py

@Author     : hsn

@Date       : 6/15/23 12:01 PM

@Version    : 1.1.0
"""
import asyncio
import json
import ssl
import uuid
from typing import Dict

import schedule
import websockets

from src.containers import Request, ReturnData
from src.request_receiver.base_receiver import BaseReceiver
from src.util.i18n import gettext_func as _


class WebsocketsWsReceiver(BaseReceiver):
    connectors: Dict[uuid.UUID, tuple] = {}

    async def send_todo_list(self):
        """
        Send todo_list to all connectors
        :return:
        """
        # send todo_list
        for connector in self.connectors.values():
            auth_data, websocket = connector

            req = Request(path="account/get_todo_list", form={}, files=None, cookies={"auth_data": auth_data})
            rt: ReturnData = self.create_req(req)

            # return todo_list if data is not 'None'
            if rt.json_data.get('data', None):
                await websocket.send(json.dumps({"ver": 1, "type": "todo_list", "data": rt.json_data}))

    def _start(self):
        """
        The main function of WS receiver
        :return:
        """
        schedule.every(1).seconds.do(lambda: asyncio.run(self.send_todo_list()))

        self.start_ws_server(self.init_handler())

    def init_handler(self):
        async def handler(websocket):
            _id = uuid.uuid1()
            try:
                while message := await websocket.recv():
                    msg_json: dict = json.loads(message)

                    # get the path, form, cookies
                    path: str = msg_json.get("path", "")
                    form: dict = msg_json.get("form", {})
                    cookies: dict = msg_json.get("cookies", {})

                    if c := self.connectors.get(_id, None):
                        cookies['auth_data'], _ = c

                    # create request
                    req = Request(path=path, form=form, files=None, cookies=cookies)
                    rt: ReturnData = self.create_req(req)

                    # if the path is account/login, save the auth_data
                    if path.startswith('account/login') \
                            and (auth_data := rt.json_data.get('_cookies', {}).get("auth_data", {}).get("value", None)):
                        self.connectors[_id] = (auth_data, websocket)

                    # send the return data
                    await websocket.send(json.dumps({"ver": 1, "type": "response", "data": rt.json_data}))
            except websockets.ConnectionClosed:
                pass
            except json.JSONDecodeError:
                websocket.send(ReturnData(ReturnData.ERROR).json_data)
            finally:
                # remove the connector
                if _id in self.connectors:
                    self.connectors.pop(_id)

        return handler

    def start_ws_server(self, handler):
        async def main():
            ssl_kwarg = {}

            if self.global_config['/network/ssl/enabled']:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_cert = self.global_config['/network/ssl/cert']
                ssl_key = self.global_config['/network/ssl/key']

                ssl_context.load_cert_chain(ssl_cert, keyfile=ssl_key)
                ssl_kwarg = {'ssl': ssl_context}
                self.logger.debug(_('WebsocketsWsReceiver started with SSL.'))
            async with websockets.serve(handler, self.host, self.port, **ssl_kwarg):
                await asyncio.Future()  # run forever

        asyncio.run(main())

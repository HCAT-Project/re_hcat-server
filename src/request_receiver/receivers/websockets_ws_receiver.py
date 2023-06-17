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
@File       : flask_http_receiver.py

@Author     : hsn

@Date       : 4/15/23 12:01 PM

@Version    : 1.0.0
"""
import asyncio
import json

import schedule
import websockets

from src.containers import Request, ReturnData
from src.request_receiver.base_receiver import BaseReceiver


class WebsocketsWsReceiver(BaseReceiver):
    connectors = []

    async def send_todo_list(self):
        for connector in self.connectors:
            auth_data, websocket = connector
            req = Request(path="account/get_todo_list", form={}, files=None, cookies={"auth_data": auth_data})
            rt = self.create_req(req)
            if rt.json_data.get('data',None):
                await websocket.send(json.dumps({"ver": 1, "type": "todo_list", "data": rt.json_data}))

    def _start(self):
        schedule.every(1).seconds.do(lambda: asyncio.run(self.send_todo_list()))

        async def handler(websocket):
            while True:
                message = await websocket.recv()
                try:
                    msg_json = json.loads(message)
                except json.JSONDecodeError:
                    websocket.send(ReturnData(ReturnData.ERROR).json_data)
                    return
                path: str = msg_json.get("path", "")
                form = msg_json.get("form", {})
                cookies = msg_json.get("cookies", {})
                req = Request(path=path, form=form, files=None, cookies=cookies)
                rt = self.create_req(req)
                if path.startswith('account/login'):
                    auth_data = rt.json_data.get('_cookies', {}).get("auth_data", {}).get("value", None)
                    if auth_data is not None:
                        self.connectors.append((auth_data, websocket))
                await websocket.send(json.dumps(rt.json_data))

        async def main():
            async with websockets.serve(handler, "127.0.0.1", 8001):
                await asyncio.Future()  # run forever

        asyncio.run(main())

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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

"""
@File       : base_receiver.py

@Author     : hsn

@Date       : 4/14/23 7:40 PM

@Version    : 1.0.0
"""
import random
import threading

from src.containers import ReturnData
from src.util.config_parser import ConfigParser


class BaseReceiver:
    def __init__(self, callback=None, config: ConfigParser = None):
        self.callback = callback
        self.lock = threading.Lock()
        self.config = config if config is not None else ConfigParser({})
        self.host = self.config.get_from_pointer(f"/network/receivers/{type(self).__name__}/host", "127.0.0.1")
        self.port = self.config.get_from_pointer(f"/network/receivers/{type(self).__name__}/port", random.randint(10000, 65535))

    def pause(self):
        self.lock.acquire()

    def resume(self):
        self.lock.release()

    def set_callback(self, callback=None):
        self.callback = callback

    def start(self):
        threading.Thread(target=self._start, daemon=True).start()

    def _start(self):
        ...

    def create_req(self, req=None):
        self.lock.acquire()
        rt = ReturnData(ReturnData.ERROR)
        try:
            rt = self.callback(req)
        finally:
            self.lock.release()
            # format return data
            return rt

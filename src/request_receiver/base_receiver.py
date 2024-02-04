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
@File       : base_receiver.py

@Author     : hsn

@Date       : 4/14/23 7:40 PM

@Version    : 1.1.0
"""
import abc
import logging
import random
import threading

from src.containers import ReturnData
from src.util.config_parser import ConfigParser


class BaseReceiver(metaclass=abc.ABCMeta):
    def __init__(self, callback=None, config=None):
        self.callback = callback
        self.lock = threading.Lock()
        self.global_config = config if config is not None else ConfigParser({})
        self.receiver_config = ConfigParser(self.global_config.get_from_pointer(
            f'/network/receivers/{self.__class__.__name__}', {}))
        self.host: str = self.receiver_config.get_from_pointer("host", "127.0.0.1")
        self.port: int = self.receiver_config.get_from_pointer("port", random.randint(10000, 65535))
        self.enable: bool = self.receiver_config.get_from_pointer("enable", False)
        self.logger: logging.Logger = logging.getLogger(type(self).__name__)

    def pause(self):
        self.lock.acquire()

    def resume(self):
        self.lock.release()

    def set_callback(self, callback=None):
        self.callback = callback

    def start(self):
        threading.Thread(target=self._start, daemon=True).start()

    @abc.abstractmethod
    def _start(self):
        ...

    def create_req(self, req=None) -> ReturnData:
        self.lock.acquire()
        rt = ReturnData(ReturnData.ERROR)
        try:
            rt = self.callback(req)
        finally:
            self.lock.release()
        # format return data
        return rt

    def msg_handler(self, user_id, msg):
        ...

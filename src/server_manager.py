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
@File       : server_manager.py

@Author     : hsn

@Date       : 4/14/23 3:47 PM

@Version    : 1.0.0
"""
import threading
import uuid

from src.containers import Request
from src.dynamic_class_loader import DynamicClassLoader
from src.request_receiver.base_receiver import BaseReceiver
from src.server import Server
from src.util.config_parser import ConfigParser


class ServerManager:
    def __init__(self, dcl: DynamicClassLoader = None, config: ConfigParser = None):
        self.config = config if config is not None else ConfigParser({})
        self.server = {}
        if dcl is None:
            self.dcl = DynamicClassLoader()
        else:
            self.dcl = dcl
        self.receivers = {}

    def join(self, timeout: float = None):

        t = self.server.get('thread', None)
        if isinstance(t, threading.Thread):
            try:
                t.join(timeout=timeout)
            except KeyboardInterrupt:
                self.close()

    def close(self):

        s = self.server.get('server', None)
        if isinstance(s, Server):
            s.close()

    def start_server_core(self, server_kwargs: dict = None):
        if server_kwargs is None:
            server_kwargs = {}
        server_kwargs['dcl'] = self.dcl
        s = Server(**server_kwargs)
        t = threading.Thread(target=s.start)
        t.start()
        self.server = {'server': s, 'thread': t}

    def request(self, req: dict = None):
        if req is None:
            req = Request()
        return self.server['server'].request_handler(req)

    def load_receivers(self):
        for i in self.dcl.load_classes_from_group("receiver"):
            c = i(self.request, self.config)
            c.start()
            self.receivers[i.__name__] = c

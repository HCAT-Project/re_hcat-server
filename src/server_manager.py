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
import logging
import subprocess
import threading
import time

from src.containers import Request
from src.dynamic_class_loader import DynamicObjLoader
from src.server import Server
from src.util.config_parser import ConfigParser
from src.util.i18n import gettext_func as _


class ServerManager:
    def __init__(self, server_kwargs: dict = None, dol: DynamicObjLoader = None, config: ConfigParser = None):
        self.config = config if config is not None else ConfigParser({})
        self.server = {}
        if dol is None:
            self.dol = DynamicObjLoader()
        else:
            self.dol = dol
        self.receivers = {}
        self.server_kwargs = server_kwargs
        if config.get_from_pointer('/sys/auto-update', False):
            logging.info(_('Auto update enabled.'))
            threading.Thread(target=self._update_thread).start()

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

    def start(self):
        self._start_server_core(self.server_kwargs)

    def _start_server_core(self, server_kwargs: dict = None):
        if server_kwargs is None:
            server_kwargs = {}
        server_kwargs['dol'] = self.dol
        s = Server(**server_kwargs)

        # Load auxiliary events
        logging.info(_('Loading auxiliary events...'))
        self._load_auxiliary_events(s)

        t = threading.Thread(target=s.start)
        t.start()
        self.server = {'server': s, 'thread': t}

    def request(self, req: dict = None):
        if req is None:
            req = Request()
        return self.server['server'].request_handler(req)

    def load_receivers(self):
        for i in self.dol.load_classes_from_group("receiver"):
            c = i(self.request, self.config)
            c.start()
            self.receivers[i.__name__] = c

    def _load_auxiliary_events(self, s: Server):
        for class_ in self.dol.load_classes_from_group('auxiliary_events'):
            # logout
            logging.debug(_('Auxiliary event "{}" loaded.').format(class_.__name__))

            s.e_mgr.add_auxiliary_event(class_.main_event, class_)

    def _update_thread(self):
        while True:
            b_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
            local_cid = subprocess.check_output(['git', 'rev-parse', '--short', b_name])
            remote_cid = subprocess.check_output(['git', 'rev-parse', '--short', 'origin/' + b_name])
            if local_cid != remote_cid:
                self.update_server()
            time.sleep(60)

    def update_server(self):
        self.close()
        for i in self.receivers:
            i.pause()

        subprocess.check_output(['git', 'pull'])

        self.start()
        for i in self.receivers:
            i.resume()

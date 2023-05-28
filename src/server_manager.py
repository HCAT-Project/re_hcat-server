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
@File       : server_manager.py

@Author     : hsn

@Date       : 4/14/23 3:47 PM

@Version    : 1.0.0
"""
import logging
import subprocess
import threading
import time

from src.containers import Request, ReturnData
from src.dynamic_class_loader import DynamicObjLoader
from src.plugin_manager import PluginManager
from src.server import Server
from src.util.config_parser import ConfigParser
from src.util.i18n import gettext_func as _


class ServerManager:
    """
    Main class of server.
    """

    def __init__(self, server_kwargs: dict = None, dol: DynamicObjLoader = None, config: ConfigParser = None,
                 plugin_mgr: PluginManager = None):
        """

        :param server_kwargs: The kwargs of server.
        :param dol: DynamicObjLoader.
        :param config: The config of server.
        """
        # Init the variables
        self.config = ConfigParser(config) if config is not None else ConfigParser({})
        self.server = {}

        self.dol = DynamicObjLoader() if dol is None else dol
        self.plugin_mgr = PluginManager() if plugin_mgr is None else plugin_mgr
        self.receivers = {}
        self.server_kwargs = server_kwargs

        # Load update service
        if config.get_from_pointer('/sys/auto-update', False):
            logging.info(_('Auto update enabled.'))
            threading.Thread(target=self._update_thread).start()

    def join(self, timeout: float = None):
        """
        Join the server thread.
        :param timeout: The timeout of join.
        :return:
        """
        t = self.server.get('thread', None)
        if isinstance(t, threading.Thread):
            t.join(timeout=timeout)

    def close(self):
        """
        Close the server.
        :return:
        """
        s = self.server.get('server', None)
        if isinstance(s, Server):
            s.close()

    def start(self):
        """
        Start the server.
        :return:
        """
        self._start_server_core(self.server_kwargs)

    def server_forever(self):
        """
        Start the server.
        :return:
        """
        self.start()
        while True:
            try:
                self.join(0.1)
            except KeyboardInterrupt:
                self.close()
                break

    def _start_server_core(self, server_kwargs: dict = None):
        """
        Start the server core.
        :param server_kwargs: The kwargs of server.
        :return:
        """
        # Init the server args.
        if server_kwargs is None:
            server_kwargs = {}
        server_kwargs['dol'] = self.dol

        # Init the server.
        s = Server(**server_kwargs)

        # Load auxiliary events.
        logging.info(_('Loading auxiliary events...'))
        self._load_auxiliary_events(s)

        # Load plugins
        logging.info(_('Loading plugins...'))
        for plugin_info, plugin_work_folder in self.plugin_mgr.load_plugins():
            logging.info(_('The plugin "{}-{}" is loaded.')
                         .format(plugin_info.get_from_pointer('/name', 'Unknown'),
                                 plugin_info.get_from_pointer('/version', '0.0.0.0')))

        # Start the thread of server.
        t = threading.Thread(target=s.server_forever, name='ServerThread')
        t.start()
        self.server = {'server': s, 'thread': t}

    def request(self, req: Request = None) -> ReturnData:
        """
        The handler of request.
        :param req: The request.
        :return:
        """
        if req is None:
            req = Request()
        return self.server['server'].request_handler(req)

    def load_receivers(self):
        """
        Load receivers.
        :return:
        """
        for i in self.dol.load_objs_from_group("receiver"):
            receiver = i(self.request, self.config)
            receiver.start()
            self.receivers[i.__name__] = receiver

    def _load_auxiliary_events(self, s: Server):
        """
        Load auxiliary events.
        :param s: The server.
        :return:
        """
        for class_ in self.dol.load_objs_from_group('auxiliary_events'):
            # logout
            logging.debug(_('Auxiliary event "{}" loaded.').format(class_.__name__))

            s.e_mgr.add_auxiliary_event(event=class_)

    def _update_thread(self):
        """
        WARN: This function is untested.
        :return:
        """
        while True:
            b_name = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True,
                                    check=True).stdout.strip()
            local_cid = subprocess.run(['git', 'rev-parse', '--short', b_name], capture_output=True, text=True,
                                       check=True).stdout.strip()
            remote_cid = subprocess.run(['git', 'rev-parse', '--short', 'origin/' + b_name], capture_output=True,
                                        text=True, check=True).stdout.strip()
            if local_cid != remote_cid:
                self.update_server()
            time.sleep(60)

    def update_server(self):
        """
        WARN: This function is untested.
        :return:
        """
        self.close()
        for i in self.receivers:
            i.pause()

        subprocess.run(['git', 'pull'], check=True)

        self.start()
        for i in self.receivers:
            i.resume()

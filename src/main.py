#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : main.py

@Author     : hsn

@Date       : 2023/3/1 下午8:35

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
import os.path
import subprocess
import sys
from pathlib import Path

from src.dynamic_class_loader import DynamicObjLoader
from src.server_manager import ServerManager
from src.util import multi_line_log
from src.util.config_parser import ConfigParser
from src.util.i18n import gettext_func as _


def get_start_arg(default_list):
    # init the args obj
    class Object:
        def __getitem__(self, item):
            return getattr(self, item)

    arg = Object()

    # set default list
    for i in default_list:
        setattr(arg, i, default_list[i])

    # load the bool arg
    for _i in range(len(sys.argv)):
        i = sys.argv[_i]
        if i.startswith('-') and not i.startswith('--'):
            value = sys.argv[_i + 1]
            if i[1:] in default_list:
                value = type(default_list[i[1:]])(value)
            setattr(arg, i[1:], value)

    # load the str arg
    for i in sys.argv:
        if i.startswith('--'):
            setattr(arg, i[2:], True)

    return arg


def load_config(path):
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def clone_client(branch='master'):
    try:
        if not os.path.exists('static'):
            multi_line_log(logger=logging.getLogger('git'), msg=subprocess.check_output(
                ['git', 'clone', 'https://github.com/HCAT-Project/hcat-client.git', 'static'],
                stderr=subprocess.DEVNULL).decode('utf8'))
        try:
            multi_line_log(logger=logging.getLogger('git'),
                           msg=subprocess.check_output(['git', 'checkout', '-b', branch, f'origin/{branch}'],
                                                       cwd='static', stderr=subprocess.DEVNULL).decode('utf8'))
        except subprocess.CalledProcessError:
            multi_line_log(logger=logging.getLogger('git'),
                           msg=subprocess.check_output(['git', 'checkout', branch], cwd='static',
                                                       stderr=subprocess.DEVNULL).decode('utf8'))
        multi_line_log(logger=logging.getLogger('git'),
                       msg=subprocess.check_output(['git', 'pull', '--force'], cwd='static',
                                                   stderr=subprocess.DEVNULL).decode('utf8'))
    except FileExistsError:
        pass


def main():
    arg = get_start_arg({'debug': False, 'config': 'config.json', 'host': '0.0.0.0', 'port': 8080, 'name': 'server'})

    # get config
    logging.getLogger().info(_('Loading config from {}').format(arg['config']))
    config_path = arg['config']
    config = load_config(config_path)

    # try to clone client
    logging.getLogger().info(_('Cloning client from github...'))
    try:
        if config['client'].get('client-branch', None) is not None:
            clone_client(config['client']['client-branch'])
    except KeyError:
        pass

    dcl = DynamicObjLoader()

    dcl.add_path_to_group("receiver", Path.cwd() / 'src/request_receiver/receivers')
    dcl.add_path_to_group("auxiliary_events", Path.cwd() / 'src/event/auxiliary_events')
    dcl.add_path_to_group("req_events", Path.cwd() / 'src/event/events')

    # init and start server
    server_kwargs = (lambda **kwargs: kwargs)(
        debug=arg['debug'],
        config=config,
        name=arg['name']
    )
    server_manager = ServerManager(server_kwargs=server_kwargs, dol=dcl, config=ConfigParser(config))

    server_manager.start()
    server_manager.load_receivers()

    server_manager.join()

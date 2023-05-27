#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : main.py

@Author     : hsn

@Date       : 2023/3/1 下午8:35

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
import datetime
import json
import logging
import os.path
import subprocess
import sys
import time
from os import PathLike
from pathlib import Path
from typing import Any

import git.exc

from git import Repo
from src.dynamic_class_loader import DynamicObjLoader
from src.plugin_manager import PluginManager
from src.server_manager import ServerManager
from src.util import multi_line_log
from src.util.command_parser import Command
from src.util.config_parser import ConfigParser
from src.util.i18n import gettext_func as _
from src.util.multi_thread import run_by_multi_thread


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
        return ConfigParser(json.load(f))


def clone_client(repo_url="https://github.com/HCAT-Project/hcat-client.git",
                 folder: str | Path = 'static', branch='master',
                 cmds=None):
    def run_check_output(cmd_: list | str, cwd: str | bytes | PathLike[str] | PathLike[bytes] | None = None) -> Any:
        return subprocess.check_output(cmd_, cwd=cwd, stderr=subprocess.DEVNULL).decode('utf8')

    def run_and_logout(cmd_: list | str, cwd: str | bytes | PathLike[str] | PathLike[bytes] | None = None):
        multi_line_log(logger=logging.getLogger('git'), msg=run_check_output(cmd_, cwd=cwd))

    if isinstance(folder, str):
        folder = Path(folder)

    if cmds is None:
        cmds = []
    if folder.exists():

        repo = Repo(folder)
        if repo.git.remote('get-url', 'origin') != repo_url:
            repo.git.remote('set-url', 'origin', repo_url)

    else:
        repo = Repo.clone_from(repo_url, folder)
    try:
        repo.git.checkout('-b', branch, f'origin/{branch}')
    except git.exc.GitCommandError:
        repo.git.checkout(branch)

    repo.remote().pull()

    for cmd in cmds:
        run_and_logout(Command(cmd, cmd_header='').cmd_list, cwd=folder)

def main():
    start_time = time.time()
    arg = get_start_arg({'debug': False, 'config': 'config.json', 'name': 'server'})

    # check debug mode
    debug = arg['debug']

    # set logger
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='[%(asctime)s][%(filename)s(%(lineno)d)][%(levelname)s] %(message)s',
                        datefmt='%b/%d/%Y-%H:%M:%S')

    # create logs folder
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # format the time
    now = datetime.datetime.now()
    formatted_time = now.strftime("%m-%d-%Y_%H:%M:%S")

    # add file handler
    handler = logging.FileHandler(
        os.path.join('logs', f'log_{formatted_time}_{int(now.now().timestamp() % 1 * 10 ** 6)}.log').replace(':', '_'),
        encoding='utf8')
    logging.getLogger().addHandler(handler)
    # get config
    logging.getLogger().info(_('Loading config from {}').format(arg['config']))
    config_path = arg['config']
    config = load_config(config_path)

    # try to clone client
    repo = config.get_from_pointer('/client/repo', 'https://github.com/HCAT-Project/hcat-client.git')
    logging.getLogger().info(_('Cloning client from github...'))
    logging.getLogger().info(_('Repo: {}').format(repo))
    try:
        if config['client'].get('client-branch', None) is not None:
            client_folder = Path(config.get_from_pointer('/client/client-folder', 'static'))

            @run_by_multi_thread(enable=Path(client_folder).exists())
            def __():
                clone_client(
                    repo_url=repo,
                    folder=client_folder,
                    branch=config['client']['client-branch'],
                    cmds=config.get_from_pointer('/client/cmds-after-update', None)
                )
    except KeyError:
        pass

    dcl = DynamicObjLoader()

    dcl.add_path_to_group("receiver", Path.cwd() / 'src/request_receiver/receivers')
    dcl.add_path_to_group("auxiliary_events", Path.cwd() / 'src/event/auxiliary_events')
    dcl.add_path_to_group("req_events", Path.cwd() / 'src/event/events')

    p_mgr = PluginManager(config=config, dcl=dcl)
    # init and start server
    server_kwargs = (lambda **kwargs: kwargs)(
        debug=arg['debug'],
        config=config,
        name=arg['name']
    )
    server_manager = ServerManager(server_kwargs=server_kwargs, dol=dcl, config=ConfigParser(config), plugin_mgr=p_mgr)
    server_manager.start()
    server_manager.load_receivers()
    total_time = time.time() - start_time
    display_time = str(total_time).split('.')[0] + '.' + str(total_time).split('.')[1][:1]
    logging.info(_('Server started, cost {}s').format(display_time))
    while True:
        try:
            server_manager.join(0.1)
        except KeyboardInterrupt:
            server_manager.close()
            break

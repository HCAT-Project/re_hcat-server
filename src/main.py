#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：main.py

@Author     : hsn

@Date       ：2023/3/1 下午8:35

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
import sys


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


def main():
    from src.server import Server
    arg = get_start_arg({'debug': False, 'config': 'config.json', 'host': '0.0.0.0', 'port': 8080, 'name': 'server'})

    # get config
    config_path = arg['config']
    config = load_config(config_path)

    # init and start server
    s = Server(debug=arg['debug'], address=(arg['host'], arg['port']), config=config, name=arg['name'])
    s.start()

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：_main.py

@Author     : hsn

@Date       ：2023/3/1 下午8:35

@Version    : 1.0.0
"""
#  Copyright 2023. HCAT-Project-Team
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
    from server import Server
    arg = get_start_arg({'debug': False, 'config': 'config.json', 'host': '0.0.0.0', 'port': 8080})

    # get config
    config_path = arg['config']
    config = load_config(config_path)

    # init and start server
    s = Server(debug=arg['debug'], address=(arg['host'], arg['port']), config=config)
    s.start()

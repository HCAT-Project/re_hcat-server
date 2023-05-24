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
@File       : config_parser.py

@Author     : hsn

@Date       : 4/9/23 9:22 AM

@Version    : 1.0.1
"""
import copy
import json
from io import TextIOWrapper, BytesIO, BufferedRandom
from os import PathLike
from typing import IO, Union
from zipfile import ZipExtFile




class ConfigParser:

    def __init__(self, config: Union['ConfigParser', dict, PathLike, str, IO, TextIOWrapper, BytesIO, BufferedRandom]):
        if isinstance(config, dict):
            self.config: dict = config
        elif isinstance(config, (str, PathLike)):
            with open(config, 'r') as f:
                self.config: dict = json.load(f)
        elif isinstance(config, (IO, TextIOWrapper, BytesIO, BufferedRandom, ZipExtFile)):
            self.config: dict = json.load(config)
        elif isinstance(config, ConfigParser):
            self.config = config.config
        else:
            raise TypeError('config type error')

    def __contains__(self, item):
        return self.get_from_pointer(item) is not None

    def get_from_pointer(self, pointer: Union[str, int], default=None):
        json_path = str(pointer).split('/')
        json_path = list(filter(lambda x: bool(x), json_path))
        config = copy.deepcopy(self.config)

        for i in json_path:

            if config is None:
                return default
            if isinstance(config, list):
                i = int(i)
                if i >= len(config):
                    return default
                config = config[i]
            elif isinstance(config, dict):
                config = config.get(i, default)
            else:
                return default

        return config

    def __getitem__(self, item):
        return self.get_from_pointer(item)

    def __getattr__(self, item):
        return self.config.__getattribute__(item)

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        return ConfigParser(copy.deepcopy(self.config, memo))

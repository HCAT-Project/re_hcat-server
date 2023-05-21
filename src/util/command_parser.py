#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : command_parser.py

@Author     : hsn

@Date       : 2023/3/1 下午6:29

@Version    : 1.0.2
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
import copy
from types import FunctionType


class Command:
    def __init__(self,
                 cmd_str: str = None,
                 sep: str = ' ',
                 control_characters: str = '"＂“”',
                 escape_func: tuple[FunctionType, FunctionType] = None,
                 max_len: int = 256,
                 cmd_header: str = '/'):
        """
        A class representing a command string.

        :param cmd_str: The command string to be parsed.
        :param sep: Separator between parameters.
        :param control_characters: A string containing the control characters to be escaped.
        :param escape_func: A tuple of escape and unescape functions, nullable.
        :param max_len: Maximum length of the command string.
        :param cmd_header: The header character for the command.
        """
        self.control_characters = control_characters
        self.cmd_header = cmd_header
        self.max_len = max_len

        # Set the escape and unescape functions, if provided.
        self.escape_func, self.unescape_func = escape_func if escape_func is not None else (None, None)
        self.sep = sep
        self.cmd_list = []

        # Load the command string, if provided.
        if cmd_str is not None:
            if not self.load(cmd_str):
                raise ValueError()

    def _escape(self, _i):
        if _i == ' ':
            return '/_'
        elif _i == '/':
            return '//'
        else:
            if _i not in self.control_characters:
                return _i
        return ''

    def load(self, cmd_str: str) -> bool:
        """
        Parse the command string and load the parameters into the command list.

        :param cmd_str: The command string to be parsed.
        :return: True if the command string was parsed successfully, False otherwise.
        """

        in_ctrl = False
        cmd_str_p = ''

        # Escape the control characters.
        for i in cmd_str:
            if i in self.control_characters:
                in_ctrl = not in_ctrl
            if in_ctrl:
                cmd_str_p += self._escape(i)
            else:
                if i not in self.control_characters:
                    cmd_str_p += i

        # # Get the prefix of the command string.
        # match_list = list(filter(lambda x: cmd_str.startswith(x), cmd_str_p))
        # if len(match_list) > 0:
        #     prefix_len = max([len(i) for i in match_list])
        # else:
        #     return False
        # ^^^^^
        # > uh..?这是什么东西啊?谁写的?
        # > * 看了看注解
        # > 啊?居然是我写的?
        # >       - hsn8086
        prefix_len = len(self.cmd_header)
        # Split the command string into parameters.
        cmd_list = cmd_str_p[prefix_len:].split(self.sep, self.max_len)

        # Unescape the parameters.
        cmd_list = list(map(lambda x: x.replace('//', '/').replace('/_', ' '), cmd_list))
        self.cmd_list = ([self.unescape_func(i) for i in cmd_list]) if (self.unescape_func is not None) else cmd_list
        return True

    def pop(self, __index=0) -> str:
        """
        Pop and return an item from the command list.

        :param __index: The index of the item to be popped.
        :return: The popped item.
        """
        if len(self.cmd_list) > 0:
            return self.cmd_list.pop(__index=__index)
        else:
            return ''

    def __getitem__(self, item):
        if isinstance(item, int):

            if item < len(self.cmd_list):
                return self.cmd_list[item]
            else:
                return ''
        rt_cmd = copy.deepcopy(self)
        rt_cmd.cmd_list = rt_cmd.cmd_list[item]
        return rt_cmd

    def __setitem__(self, key, value):
        return self.cmd_list.__setitem__(key, value)

    def __delitem__(self, key):
        return self.cmd_list.__delitem__(key)

    def __len__(self):
        return self.cmd_list.__len__()

    def __iter__(self):
        return self.cmd_list.__iter__()

    def __reversed__(self):
        return self.cmd_list.__reversed__()

    def __contains__(self, item):
        return self.cmd_list.__contains__(item)

    def __str__(self):
        return self.sep.join(self.cmd_list)

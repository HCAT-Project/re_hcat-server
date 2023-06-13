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
@File       : functools.py

@Author     : hsn

@Date       : 6/13/23 8:56 PM

@Version    : 1.0.0
"""
from typing import Any


def decorator_with_parameters(func):
    def wrapper(*args, **kwargs):
        def wrapper2(func_):
            return func(func_, *args, **kwargs)

        return wrapper2

    return wrapper


def mulitdispatchmethod(func):
    class MultiDispatchMethod:
        def __init__(self, default_func):
            self.default = default_func
            self.func_dict = {}

            @decorator_with_parameters
            def _(func_, *types):
                self.func_dict[types] = func_

            self.register = _

        def __call__(self, *args):
            types = tuple(arg.__class__ for arg in args)
            for k, v in self.func_dict.items():
                if len(k) != len(types):
                    continue
                for ft, t in zip(k, types):
                    if ft == Any:
                        continue
                    if not issubclass(t, ft):
                        break
                else:
                    matched_func = v
                    break
            else:
                matched_func = self.default
            return matched_func(*args)

    return MultiDispatchMethod(func)

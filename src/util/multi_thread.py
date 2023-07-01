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
@File       : multi_thread.py

@Author     : hsn

@Date       : 5/20/23 8:33 PM

@Version    : 1.0.1
"""
import threading

import src.util.functools


@src.util.functools.decorator_with_parameters
def run_by_multi_thread(func, enable=True):
    if enable:
        thread = threading.Thread(target=func)
        thread.start()
    else:
        func()

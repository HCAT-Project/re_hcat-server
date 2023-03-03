#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：jelly.py

@Author     : hsn

@Date       ：2023/3/1 下午9:02

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


# Copyright 2023. hsn
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
class Jelly:
    """
    A class for pickling and unpickling instances of itself
    """

    # auther: hsn
    # data: 01/15/2023(MM/DD/YYYY)
    # ver: 2.0
    def __init__(self):
        self._var_init()

    def _var_init(self):
        # Initialize instance variables
        ...

    def _get_instance_variables(self) -> list:
        """
        Get a list of all non-method instance variables
        """
        return [i for i in dir(self) if not i.startswith('__') and not callable(getattr(self, i))]

    def __getstate__(self):
        """
        Get the state of the object for pickling
        """
        state = {k: getattr(self, k) for k in self._get_instance_variables()}
        return state

    def __setstate__(self, state):
        """
        Set the state of the object after unpickling
        """
        state = state
        self._var_init()
        for k, v in state.items():
            setattr(self, k, v)

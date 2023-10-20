#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : jelly.py

@Author     : hsn

@Date       : 01/15/2023(MM/DD/YYYY)

@Version    : 2.0.1

@Description: A class for pickling and unpickling instances of itself
"""
from collections.abc import MutableSet, Hashable
from typing import Mapping, Any


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

        # set => list
        sg = map(lambda x: (
            x[0], {"_obj_type": ".UserSet", "data": list(x[1])}
            if isinstance(x[1], (set, UserSet))
            else x[1]
        ), state.items())

        return dict(sg)

    def __setstate__(self, state):
        """
        Set the state of the object after unpickling
        """
        self._var_init()

        for k, v in state.items():
            if isinstance(v, dict) and "_obj_type" in v:
                v = jelly_load(v)

            setattr(self, k, v)


class UserSet(Hashable, MutableSet, Jelly):
    """
    A set of users.

    From: https://stackoverflow.com/a/58348971/21099289 Thank you so much!!!
    """
    __hash__ = MutableSet._hash

    class DataDescriptor:
        def __init__(self, name):
            self.name = name

        def __get__(self, instance, owner):
            return instance.__dict__[self.name]

        def __set__(self, instance, value):
            instance.__dict__[self.name] = set(value)

    data = DataDescriptor('data')

    def __init__(self, iterable=()):
        super().__init__()
        self.data = iterable

    def __contains__(self, value):
        return value in self.data

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return repr(self.data)

    def add(self, item):
        self.data.add(item)

    def discard(self, item):
        self.data.discard(item)


def jelly_dump(_class: Jelly):
    return {'_obj_type': f'{_class.__module__}.{_class.__class__.__name__}', **_class.__getstate__()}


def jelly_load(_dict: Mapping[str, Any]):
    if (name := _dict['_obj_type'].rsplit('.', 1))[0]:
        module_name, class_name = name
        module = __import__(module_name, fromlist=[class_name])
        class_ = getattr(module, class_name)
    else:
        class_name = name[1]
        class_ = globals()[class_name]

    obj = class_.__new__(class_)
    obj.__setstate__(_dict)
    return obj

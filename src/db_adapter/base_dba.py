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
@File       : base_dba.py

@Author     : hsn

@Date       : 5/28/23 9:34 AM

@Version    : 1.0.0
"""
import abc
import typing
from contextlib import contextmanager

from src.util.functools import mulitdispatchmethod


class Item:
    def __init__(self, key, value):
        self.init_finish = False
        self.__key = key
        self.value = value
        self.init_finish = True

    @property
    def key(self):
        return self.__key


class BaseDBA(metaclass=abc.ABCMeta):
    """
    DateBase adapter base class.
    """

    @abc.abstractmethod
    def get(self, key):
        """
        Get a value from database.
        """
        pass

    @abc.abstractmethod
    @mulitdispatchmethod
    def set(self, key, value) -> bool:
        """
        Default func of `set`.
        Recommend to use `@src.util.functools.mulitdispatchmethod` to init and use `set.register` to register a new type.
        You can also use as type error handler.
        """
        pass

    @set.register(Item)
    def _(self, item: Item) -> bool:
        """
        Set a Item to database.
        This func is an example.
        """
        return self.set(item.key, item.value)

    @abc.abstractmethod
    def rem(self, key) -> bool:
        """
        Remove a value from database.
        """
        pass

    @contextmanager
    def enter(self, key) -> typing.Generator[Item, None, None]:
        """
        Enter a value from database.
        Example:
            @contextmanager
            def enter(self, key):
                r = 0
                i = Item(0, r)
                yield i
                r = i.value
                print(r)
        """

        i = Item(key, self.get(key))
        yield i
        if i.value is None:
            self.rem(i.key)
        else:
            self.set(i)

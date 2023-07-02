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
import copy
import typing
from contextlib import contextmanager
from typing import Mapping, Any, List


class Item:
    def __init__(self, id_, document: Mapping[str, Any]):
        self.init_finish = False
        self.__id = id_
        self.value = document
        self.init_finish = True

    @property
    def id(self):
        return self.__id

    def get(self, key: str, default: Any = None):
        return self.value.get(key, default)

    def __getitem__(self, item):
        return self.value[item]

    def __setitem__(self, key, value):
        self.value[key] = value


class BaseDBA(metaclass=abc.ABCMeta):
    """
    DateBase adapter base class.
    """

    @abc.abstractmethod
    def find(self,
             filter_: Mapping[str, Any],
             masking: Mapping[str, Any] = None,
             limit: int = None,
             sort_key: str = None) -> List[Item]:
        """
        Get values from database.
        :param filter_:
        :param masking:
        :param limit:
        :param sort_key:
        :return:
        """

        pass

    def find_one(self,
                 filter_: Mapping[str, Any],
                 masking: Mapping[str, Any] = None,
                 sort_key: str = None) -> (Item | None):
        """
        Get a value from database.
        :param filter_:
        :param masking:
        :param sort_key:
        :return:
        """
        if v_p := self.find(filter_=filter_, masking=masking, limit=1, sort_key=sort_key):
            v = v_p[0]
            return v
        else:
            return None

    @abc.abstractmethod
    def insert(self, item: Item) -> bool:
        """
        Insert a value to database.
        :param item:
        :return:
        """
        pass

    @abc.abstractmethod
    def update_one(self, filter_: Mapping[str, Any],
                   update: Mapping[str, Any]):
        """
        Update a value from database.
        :param filter_:
        :param update:
        :return:
        """
        pass

    def update_many(self,
                    filter_: Mapping[str, Any],
                    update: Mapping[str, Any]):
        while self.find_one(filter_=filter_):
            self.update_one(filter_=filter_, update=update)

    @abc.abstractmethod
    def delete_one(self, filter_: Mapping[str, Any]):
        """
        Delete a value from database.
        :param filter_:
        :return:
        """
        pass

    def delete_many(self, filter_: Mapping[str, Any]):
        while self.find_one(filter_=filter_):
            self.delete_one(filter_=filter_)

    @abc.abstractmethod
    def save(self, item: Item) -> bool:
        """
        Save a value to database.
        :param item:
        :return:
        """
        pass

    @contextmanager
    def enter_one(self, filter_: Mapping[str, Any]) -> typing.Generator[Item, None, None]:
        """
        Enter a value from database.
        """

        i = self.find_one(filter_=filter_)
        old_v = copy.deepcopy(i.value)
        yield i
        if i.value is None:
            self.delete_one(filter_=old_v)
        else:
            set_list = filter(lambda k, v: v != old_v.get(k), i.value.items())
            self.update_one(filter_=old_v, update=dict(set_list))

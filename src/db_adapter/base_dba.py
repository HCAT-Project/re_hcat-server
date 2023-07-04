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
from collections import UserDict
from contextlib import contextmanager
from typing import Mapping, Any, Iterable

from src.util.config_parser import ConfigParser


class Item(UserDict):
    def __init__(self, document: Mapping[str, Any] | None):
        super().__init__(document)
        self.value = self.data

    def __repr__(self):
        return f'{self.__class__.__name__}({super().__repr__()})'


class BaseCA(metaclass=abc.ABCMeta):
    """
    DateBase adapter base class.
    """

    def __init__(self, global_config: ConfigParser, config: ConfigParser, collection: str):
        self.global_config = global_config
        self.config = config
        self.collection = collection

    @abc.abstractmethod
    def find(self,
             filter_: Mapping[str, Any] = None,
             masking: Mapping[str, Any] = None,
             limit: int = None,
             sort_key: str = None) -> Iterable[Item]:
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
                 filter_: Mapping[str, Any] = None,
                 masking: Mapping[str, Any] = None) -> (Item | None):
        """
        Get a value from database.
        :param filter_:
        :param masking:
        :return:
        """
        if v_p := list(self.find(filter_=filter_, masking=masking, limit=1, sort_key=sort_key)):
            v = v_p[0]
            return v
        else:
            return None

    @abc.abstractmethod
    def insert_one(self, item: Item | Mapping[str, Any]):
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
    def enter_one(self, filter_: Mapping[str, Any] | None) -> typing.Generator[Item, None, None]:
        """
        Enter a value from database.
        """

        i = self.find_one(filter_=filter_)

        if i.value is not None:
            old_v = copy.deepcopy(i.value)

            yield i
            if i.value is None:
                self.delete_one(filter_=old_v)
            else:

                set_list = filter(lambda x: x[1] != old_v.get(x[0]), i.value.items())
                if upd := dict(set_list):
                    self.update_one(filter_=old_v, update={'$set': upd})
        else:
            i = Item(None)
            yield i
            if i.value is not None:
                self.insert_one(item=i)


class BaseDBA(metaclass=abc.ABCMeta):
    def __init__(self, config: ConfigParser):
        self.global_config = config
        self.config = ConfigParser(config.get_from_pointer(f'/db/adapters/{self.__class__.__name__}'))

    @abc.abstractmethod
    def get_collection(self, collection: str) -> BaseCA:
        """
        Get a collection from database.
        :param collection:
        :return:
        """
        pass

    def __getitem__(self, item) -> BaseCA:
        return self.get_collection(item)

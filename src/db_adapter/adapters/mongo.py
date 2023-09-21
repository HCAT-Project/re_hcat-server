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
@File       : mongo.py

@Author     : hsn

@Date       : 6/20/23 16:34 PM

@Version    : 1.0.0
"""
from typing import Mapping, Any, Iterable

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.db_adapter.base_dba import BaseCA, BaseDBA, Item
from src.util.config_parser import ConfigParser


class MongoCA(BaseCA):

    def __init__(self, global_config: ConfigParser, config: ConfigParser, collection: str, db: Database):
        super().__init__(global_config=global_config, config=config, collection=collection)
        self._collection: Collection = db[collection]

    def update_one(self, filter_: Mapping[str, Any], update: Mapping[str, Any]):
        self._collection.update_one(filter_, update)

    def delete_one(self, filter_: Mapping[str, Any]):
        self._collection.delete_one(filter_)

    def save(self, item: Item) -> bool:
        return self._collection.save(item.data)

    def find(self, filter_: Mapping[str, Any], masking=None, limit: int = 0,
             sort_key: str = "") -> Iterable[Item]:
        rt = self._collection.find(filter_ if filter_ else {}, masking).limit(limit)
        if sort_key:
            rt = rt.sort(sort_key)
        return rt

    def insert_one(self, item: Item | Mapping[str, Any]):
        v = item
        while isinstance(item, Item):
            v = item.data

        self._collection.insert_one(v)

    def find_one(self,
                 filter_: Mapping[str, Any],
                 masking=None) -> (Item | None):
        i = self._collection.find_one(filter_, masking)

        if i is None:
            return Item(None)
        return Item(i)


class Mongo(BaseDBA):
    def __init__(self, config: ConfigParser):
        super().__init__(config)
        self.collections = {}

    def close(self):
        pass

    def get_collection(self, collection: str) -> BaseCA:
        if collection in self.collections:
            return self.collections[collection]
        else:
            db: Database[Mapping[str, Any] | Any] = MongoClient(host=self.config['host'], port=self.config['port'])[
                self.config['db']]
            ca = MongoCA(global_config=self.global_config, config=self.config, collection=collection, db=db)
            self.collections[collection] = ca
            return ca

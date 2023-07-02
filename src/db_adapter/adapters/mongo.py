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
from pymongo.database import Database

from src.db_adapter.base_dba import BaseCA, BaseDBA, Item
from src.util.config_parser import ConfigParser


class MongoCA(BaseCA):

    def __init__(self, global_config: ConfigParser, config: ConfigParser, collection: str, db: Database):
        super().__init__(global_config=global_config, config=config, collection=collection)
        self._collection = db[collection]

    def update_one(self, filter_: Mapping[str, Any], update: Mapping[str, Any]):
        self._collection.update_one(filter_, update)

    def delete_one(self, filter_: Mapping[str, Any]):
        self._collection.delete_one(filter_)

    def save(self, item: Item) -> bool:
        return self._collection.save(item.value)

    def find(self, filter_: Mapping[str, Any], masking: Mapping[str, Any] = None, limit: int = None,
             sort_key: str = None) -> Iterable[Item]:
        return self._collection.find(filter_, masking, limit, sort_key)

    def insert(self, item: Item) -> bool:
        return self._collection.insert(item.value)

    def find_one(self,
                 filter_: Mapping[str, Any],
                 masking: Mapping[str, Any] = None,
                 sort_key: str = None) -> (Item | None):
        return self._collection.find_one(filter_, masking, sort_key)


class Mongo(BaseDBA):

    def get_collection(self, collection: str) -> BaseCA:
        db = MongoClient(host=self.config['host'], port=self.config['port'])[self.config['db']]
        return MongoCA(global_config=self.global_config, config=self.config, collection=collection, db=db)

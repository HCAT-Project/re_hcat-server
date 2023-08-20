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
@File       : zo.py

@Author     : hsn

@Date       : 8/18/23 8:53 PM

@Version    : 1.0.0
"""
import uuid
from pathlib import Path

from ZODB.FileStorage import FileStorage

from src.util.config_parser import ConfigParser

# !/usr/bin/env python
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

from src.db_adapter.base_dba import BaseCA, BaseDBA, Item
from ZODB import DB

import transaction


class ZoCA(BaseCA):
    def __init__(self, global_config: ConfigParser, config: ConfigParser, collection: str):
        super().__init__(global_config, config, collection)
        path_str = self.config.get("path", None)
        if path_str:
            path = Path(path_str) / f'{collection}.fs'
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            self.storage = FileStorage(path.as_posix())
        else:
            self.storage = None

        self.db = DB(self.storage)
        self.connection = self.db.open()
        self.conn = self.connection.root()
        print(self.conn)

    def find(self, filter_: Mapping[str, Any] | None = None, masking: Mapping[str, Any] | None = None, limit: int = 0,
             sort_key: str = "") -> \
            Iterable[Item]:
        if filter_ is None:
            filter_ = {}
        if masking is None:
            masking = {}
        for i, v in self.conn.items():

            for f in filter_:
                if f not in v:
                    break
                if v[f] != filter_[f]:
                    break
            else:
                yield Item(dict(filter(lambda x: masking.get(x[0], True), v.items())))

    def insert_one(self, item: Item | Mapping[str, Any]):
        v = item
        while isinstance(item, Item):
            v = item.data
        if "_id" in v:
            _id = v["_id"]
        else:
            _id = uuid.uuid4().hex
            v = {**v, "_id": _id}
        self.conn[_id] = v
        transaction.commit()

    def update_one(self, filter_: Mapping[str, Any], update: Mapping[str, Any]):
        v = self.find_one(filter_)
        if v:
            _id = v["_id"]
            print(update)
            rt = v.data
            rt.update(update.get("$set", {}))
            self.conn[_id] = rt
            transaction.commit()
            print(self.conn[_id])
        else:
            self.insert_one(update)

    def delete_one(self, filter_: Mapping[str, Any]):
        v = self.find_one(filter_)
        if v:
            _id = v["_id"]
            del self.conn[_id]
            transaction.commit()

    def save(self, item: Item) -> bool:
        try:
            self.insert_one(item)
        except Exception:
            return False
        else:
            return True


class Zo(BaseDBA):
    def __init__(self, config: ConfigParser):
        super().__init__(config)
        self.dbs: dict[str, ZoCA] = {}

    def close(self):
        for i in self.dbs:
            print(i)
            if not transaction.get().isDoomed():
                transaction.commit()
            self.dbs[i].connection.close()
            self.dbs[i].db.close()
            self.dbs[i].storage.close()

    def get_collection(self, collection: str) -> BaseCA:
        if collection not in self.dbs:
            db = ZoCA(global_config=self.global_config, config=self.config, collection=collection)
            self.dbs[collection] = db
        else:
            db = self.dbs[collection]
        return db

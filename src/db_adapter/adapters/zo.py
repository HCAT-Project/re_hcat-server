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


class ZoCA(BaseCA):
    def __init__(self, global_config: ConfigParser, config: ConfigParser, collection: str):
        super().__init__(global_config, config, collection)
        path_str = self.config.get("path", None)
        if path_str:
            path = Path(path_str) / f'{collection}.fs'
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            storage = FileStorage(path.as_posix())
        else:
            storage = None

        db = DB(storage)
        connection = db.open()
        self.db = connection.root()
        print(self.db)

    def find(self, filter_: Mapping[str, Any] | None = None, masking: Mapping[str, Any] | None = None, limit: int = 0,
             sort_key: str = "") -> \
            Iterable[Item]:
        for i in self.db:
            for f in filter_:
                if f not in i:
                    break
                if i[f] != filter_[f]:
                    break
            else:
                yield Item(dict(filter(lambda x: masking.get(x[0], False), i.items())))

    def insert_one(self, item: Item | Mapping[str, Any]):
        v = item
        while isinstance(item, Item):
            v = item.data
        if "_id" in v:
            _id = v["_id"]
        else:
            _id = uuid.uuid4().hex
            v = {**v, "_id": _id}
        self.db[_id] = v

    def update_one(self, filter_: Mapping[str, Any], update: Mapping[str, Any]):
        v = self.find_one(filter_)
        if v:
            _id = v["_id"]
            rt = v.data
            rt.update(update)
            self.db[_id] = rt
        else:
            self.insert_one(update)

    def delete_one(self, filter_: Mapping[str, Any]):
        v = self.find_one(filter_)
        if v:
            _id = v["_id"]
            del self.db[_id]

    def save(self, item: Item) -> bool:
        try:
            self.insert_one(item)
        except Exception:
            return False
        else:
            return True


class Zo(BaseDBA):

    def get_collection(self, collection: str) -> BaseCA:
        return ZoCA(global_config=self.global_config, config=self.config, collection=collection)

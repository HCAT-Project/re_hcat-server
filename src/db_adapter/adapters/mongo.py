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

from pymongo import MongoClient

from src.db_adapter.base_dba import BaseDBA


class Mongo(BaseDBA):
    def __init__(self,config):


    def get(self, key):
        pass

    def set(self, key, value) -> bool:
        pass

    def rem(self, key) -> bool:
        pass


if __name__=='__main__':
    mgct=MongoClient(host='127.0.0.1')

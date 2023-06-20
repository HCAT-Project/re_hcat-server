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
@File       : db_manager.py

@Author     : hsn

@Date       : 6/20/23 16:47 PM

@Version    : 1.0.0
"""
from src.dynamic_obj_loader import DynamicObjLoader
from src.util.config_parser import ConfigParser


class DBManager:
    def __init__(self,db:str, config: ConfigParser, dol: DynamicObjLoader = None):
        self.config = config
        self.dol = dol if dol is not None else DynamicObjLoader
        self.db=dol.load_obj_from_group(path=db,group=)



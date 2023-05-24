#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Copyright (C) 2023. HCAT-Project-Team
#  _
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  _
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  _
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
@File       : dynamic_class_loader.py

@Author     : hsn

@Date       : 4/14/23 7:44 PM

@Version    : 1.0.1
"""
import importlib
from pathlib import Path, PosixPath
from typing import Union

import pysnooper

import src.util.text


class DynamicObjLoader:
    def __init__(self):

        self.group_dict = {}

    @staticmethod
    def load_obj(path: str | PosixPath, obj_name: str = None):
        if isinstance(path, Path):
            path = str(path)
        if obj_name is None:
            obj_name = src.util.text.under_score_to_pascal_case(Path(path).stem)

        try:
            m_name = f'{path.replace("/", ".").rstrip(".py")}'
            # get the module
            module_ = importlib.import_module(m_name)

            # get the class of the event
            obj_ = getattr(module_, obj_name)

        except ImportError:
            return None

        return obj_

    def load_objs(self, path: Union[str, Path]):
        modules_dir = path if isinstance(path, Path) else Path(path)

        for i in filter(lambda p: p.suffix == '.py', modules_dir.iterdir()):
            if i.is_dir():
                yield from self.load_objs(i)
            else:
                obj_name = src.util.text.under_score_to_pascal_case(i.stem)
                rt_obj = self.load_obj(i.relative_to(Path.cwd()).as_posix(), obj_name)
                if rt_obj is not None:
                    yield rt_obj

    def load_objs_from_group(self, group: str = "default"):
        for i in self.group_dict.get(group, []):
            yield from self.load_objs(i)

    def load_obj_from_group(self, path: Union[str, Path], obj_name: str = None, group: str = "default"):
        for i in self.group_dict.get(group, []):
            module_path = Path(i) / path
            if module_path.with_suffix(".py").exists():
                if isinstance(module_path, PosixPath):
                    module_path = module_path.resolve()
                return self.load_obj(module_path.relative_to(Path.cwd()).as_posix(), obj_name=obj_name)
        return None

    def add_path_to_group(self, group: str = "default", path: Union[str, Path] = None):
        path_ = path if isinstance(path, str) else path.as_posix()
        existing = self.group_dict.get(group, [])
        existing.append(path_)
        self.group_dict[group] = existing

    def del_path_from_group(self, group: str = "default", path: Union[str, Path] = None):
        path_ = path if isinstance(path, str) else path.as_posix()
        existing = self.group_dict.get(group, [])
        existing.remove(path_)
        self.group_dict[group] = existing

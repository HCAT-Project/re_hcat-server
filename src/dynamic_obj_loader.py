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
@File       : dynamic_obj_loader.py

@Author     : hsn

@Date       : 4/14/23 7:44 PM

@Version    : 1.0.1
"""
import importlib
from pathlib import Path, PosixPath
from typing import Union

import src.util.text


class DynamicObjLoader:
    def __init__(self):

        self.group_dict = {}

    @staticmethod
    def load_obj(path: str | PosixPath, obj_name: str = "", *, _type: type = None):
        path = str(path)
        if obj_name == "":
            obj_name = src.util.text.under_score_to_pascal_case(Path(path).stem)

        m_name = f'{path.replace("/", ".").replace(".py", "")}'

        # get the module
        module_ = importlib.import_module(m_name)

        # get the class of the event
        obj_ = getattr(module_, obj_name)

        if _type is not None and not isinstance(obj_, _type):
            print(obj_, _type)
            raise TypeError(f"obj {obj_name} in {path} is not a {_type}")

        return obj_

    def load_objs(self, path: Union[str, Path], *, _type: type = None):
        modules_dir = path if isinstance(path, Path) else Path(path)

        for i in filter(lambda p: p.suffix == '.py', modules_dir.iterdir()):
            if i.is_dir():
                yield from self.load_objs(path=i, _type=_type)
            else:
                obj_name = src.util.text.under_score_to_pascal_case(name=i.stem)

                try:
                    rt_obj = self.load_obj(path=i.relative_to(Path.cwd()).as_posix(), obj_name=obj_name, _type=_type)
                except ImportError:
                    continue

                if rt_obj is not None:
                    yield rt_obj

    def load_objs_from_group(self, group: str = "default", *, _type: type = None):
        for i in self.group_dict.get(group, []):
            yield from self.load_objs(i, _type=_type)

    def load_obj_from_group(self, path: Union[str, Path], obj_name: str = "", group: str = "default", *,
                            _type: type = None):
        for i in self.group_dict.get(group, []):
            module_path = Path(i) / path
            if module_path.with_suffix(".py").exists():
                module_path = module_path.resolve()

                return self.load_obj(module_path.relative_to(Path.cwd()).as_posix(), obj_name=obj_name, _type=_type)
        return None

    def add_path_to_group(self, group: str = "default", path: Union[str, Path] = ""):
        path_ = path if isinstance(path, str) else path.as_posix()
        existing = self.group_dict.get(group, [])
        existing.append(path_)
        self.group_dict[group] = existing

    def del_path_from_group(self, group: str = "default", path: Union[str, Path] = ""):
        path_ = path if isinstance(path, str) else path.as_posix()
        existing = self.group_dict.get(group, [])
        existing.remove(path_)
        self.group_dict[group] = existing

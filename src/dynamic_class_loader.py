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
@File       : dynamic_class_loader.py

@Author     : hsn

@Date       : 4/14/23 7:44 PM

@Version    : 1.0.0
"""
import hashlib
import importlib
import logging
from pathlib import Path
from typing import Union

from src import util


class DynamicClassLoader:
    def __init__(self):

        self.group_dict = {}

    @staticmethod
    def load_class(path: str, class_name: str = None):
        if class_name is None:
            class_name = util.under_score_to_pascal_case(Path(path).stem)

        try:
            # get the module
            event_module = importlib.import_module(f'{path.replace("/", ".").rstrip(".py")}')

            # get the class of the event
            event_class = getattr(event_module, class_name)

        except ImportError as err:
            return None

        return event_class

    def load_classes(self, path: Union[str, Path]):
        classes_dir = path if isinstance(path, Path) else Path(path)

        for i in filter(lambda p: p.suffix == '.py', classes_dir.iterdir()):
            if i.is_dir():
                yield from self.load_classes(i)
            else:
                class_name = util.under_score_to_pascal_case(i.stem)
                yield self.load_class(i.relative_to(Path.cwd()).as_posix(), class_name)

    def load_classes_from_group(self, group: str = "default"):
        for i in self.group_dict.get(group, []):
            yield from self.load_classes(i)

    def load_class_from_group(self, path: Union[str, Path], class_name: str = None, group: str = "default"):
        for i in self.group_dict.get(group, []):
            if (Path(i) / path).with_suffix(".py").exists():
                return self.load_class((Path(i) / path).relative_to(Path.cwd()).as_posix(), class_name=class_name)
        return None

    def add_path_to_group(self, group: str = "default", path: Union[str, Path] = None):
        path_ = path if isinstance(path, str) else path.as_posix()
        existing = self.group_dict.get(group, [])
        existing.append(path_)
        self.group_dict[group] = existing

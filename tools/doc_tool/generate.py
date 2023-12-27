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
@File       : generate.py

@Author     : hsn

@Date       : 12/26/23 6:10 PM
"""
import inspect
from pathlib import Path

from src.dynamic_obj_loader import DynamicObjLoader


def main():
    dol = DynamicObjLoader()
    objs = dol.load_objs('src/event/events')
    base_path = Path('tools/doc_tool/doc')
    for i in objs:
        p = (base_path / '/'.join(i.__module__.split('.')[3:]))

        p.parent.mkdir(parents=True, exist_ok=True)
        with Path(p.as_posix() + '.md').open('w', encoding='utf8') as f:
            for j in gen(i):
                f.write(j + '\n')


def fill(text, length=20):
    return text + ' ' * (length - len(text))


def gen(obj_):
    yield "---"
    yield "sidebar_position: 2"
    yield "---"
    yield f"# {obj_.__module__.split('.')[-1].replace('_', ' ').title()}"
    yield ""
    yield "# 描述"
    yield ""
    yield str(obj_.__doc__)
    yield ""
    yield "| 请求地址                            | 请求方式     |"
    yield "| ------------------------------------ | ------------ |"
    yield f"| {'api/' + '/'.join(obj_.__module__.split('.')[3:])}             | POST         |"
    yield ""
    yield "| 参数        | 类型               |"
    yield "| ----------- | ------------------ |"
    for i in inspect.signature(obj_).parameters.values():
        yield f"| {i.name} | {i.annotation.__name__} |"
    yield ""
    yield "| 返回参数    | 类型     |"
    yield "| ----------- | -------- |"
    obj_.returns: dict
    for i, j in obj_.returns.items():
        yield f"| {i} | {j.__name__}  |"
    yield "| status | str  |"
    yield "| message | str  |"


if __name__ == '__main__':
    main()

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
@File       : file_manager.py

@Author     : hsn

@Date       : 4/22/23 10:21 PM

@Version    : 1.0.0
"""
import time
from pathlib import Path
from typing import Union, IO
from src.util.hash_utils import file_hash


class FileManager:
    def __init__(self, path: Union[Path, str] = '/', info_db=None):
        self.info_db = info_db
        self.path = path

    def get_file_path(self, sha1: str):
        path = Path(self.path) / sha1

        return path if path.exists() else None

    def save_file(self, file: IO[bytes], timeout=7 * 24 * 60) -> str:

        hash_ = file_hash(file)
        file.seek(0)

        with open(Path(self.path) / hash_, 'wb') as f:
            while chunk := file.read(1024):
                f.write(chunk)
        with self.info_db.enter(hash_) as info:
            info.value = {'size': file.tell(), 'timeout': time.time() + timeout, 'ref': 0}
        return hash_

    def add_ref(self, sha1: str):
        with self.info_db.enter(sha1) as info:
            if not isinstance(info.value, dict):
                raise TypeError("info.value should be a dictionary")
            info.value['ref'] += 1

    def clear_timeout(self) -> int:
        i = 0
        for key in self.get_all_keys():
            print(key)
            with self.info_db.enter(key) as info:
                if info.value is None:
                    Path(key).unlink()
                    continue

                if not isinstance(info.value, dict):
                    raise TypeError("info.value should be a dictionary")

                if info.value.get('timeout', 0) < time.time() and info.value['ref'] == 0:
                    Path(key).unlink()
                    info.value = None
                    i += 1
        return i

    def get_all_keys(self):
        for file in Path(self.path).iterdir():
            yield str(file)

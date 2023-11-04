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
@File       : file_manager.py

@Author     : hsn

@Date       : 4/22/23 10:21 PM

@Version    : 1.0.0
"""
import tempfile
import time
from pathlib import Path
from typing import Union, IO

from src.util.crypto import file_hash


class FileManager:
    def __init__(self, path: Union[Path, str] = '/', info_db=None, *, mkdir=True):
        self.info_db = info_db
        self.path = Path(path)
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)

    def get_file_path(self, sha1: str):
        path = Path(self.path) / sha1

        return path if path.exists() else None

    def read_file(self, sha1: str):
        try:
            return self.get_file_path(sha1).open('rb')
        except FileNotFoundError:
            raise FileNotFoundError(f"File {sha1} not found")

    def save_file(self, file: IO[bytes], timeout=7 * 24 * 60, max_size: int = -1) -> str:
        tmp_file = tempfile.TemporaryFile()
        while chunk := file.read(1024):
            tmp_file.write(chunk)
        if tmp_file.seek(0, 2) > max_size >= 0:
            raise Exception("File too large")
        tmp_file.seek(0)
        hash_ = file_hash(tmp_file)

        tmp_file.seek(0)
        if not (Path(self.path) / hash_).exists():
            with open(Path(self.path) / hash_, 'wb') as f:
                while chunk := tmp_file.read(1024):
                    f.write(chunk)
        with self.info_db.enter_one(hash_) as info:
            info.data = {'size': file.tell(), 'timeout': time.time() + timeout, 'ref': 0}

        return hash_

    def add_ref(self, sha1: str):
        with self.info_db.enter_one(sha1) as info:
            if not isinstance(info.data, dict):
                raise TypeError("info.data should be a dictionary")
            info.data['ref'] += 1

    def clear_timeout(self) -> int:
        i = 0
        for key in self.get_all_keys():

            with self.info_db.enter_one(key) as info:
                if info.data is None:
                    Path(key).unlink()
                    continue

                if not isinstance(info.data, dict):
                    raise TypeError("info.data should be a dictionary")

                if info.data.get('timeout', 0) < time.time() and info.data['ref'] == 0:
                    Path(key).unlink()
                    info.data = None
                    i += 1
        return i

    def get_all_keys(self):
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)
        for file in self.path.iterdir():
            yield str(file)

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
@File       : hash_utils.py

@Author     : hsn

@Date       : 4/9/23 11:08 AM

@Version    : 1.0.0
"""
import _io
import hashlib
import io
import tempfile
from os import PathLike
from typing import IO, Union


def read_chunks(file: Union[str, PathLike, IO[bytes]], chunk_size: int = io.DEFAULT_BUFFER_SIZE):
    if isinstance(file, (str, PathLike)):
        f = open(file, 'rb')
    elif isinstance(file, (IO, tempfile.SpooledTemporaryFile, _io.BufferedReader)):
        f = file
    else:
        raise TypeError(f'Unsupported type {type(file)}')

    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield chunk


def file_hash(file: Union[str, PathLike, IO[bytes]]):
    h = hashlib.sha1()
    for chunk in read_chunks(file):
        h.update(chunk)
    return h.hexdigest()


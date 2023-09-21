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
@File       : bytes.py

@Author     : hsn

@Date       : 5/17/23 8:22 PM

@Version    : 1.0.0
"""
from typing import Any, Generator


def chunk_bytes(data: bytes, chunk_size=1024) -> Generator[bytes, Any, None]:
    """
    Splits bytes into chunks of specified size.

    Example:
        for chunk in chunk_bytes(data, 1024):
            process_chunk(chunk)

    :param data: The bytes to be chunked.
    :param chunk_size: The size of each chunk.

    :return: An iterator over the chunks.
    """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

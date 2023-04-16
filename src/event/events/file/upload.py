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
@File       : upload.py

@Author     : hsn

@Date       : 4/9/23 8:19 AM

@Version    : 1.0.0
"""
import hashlib
import logging
import os

from src.containers import ReturnData
from src.event.base_event import BaseEvent
from src.util.hash_utils import file_hash


class Upload(BaseEvent):
    auth = True

    def _run(self):
        _ = self.gettext_func
        # check if the file is in the request
        if 'file' not in self.req.files:
            return ReturnData(ReturnData.NULL, _('No file uploaded.'))

        # get the file
        file = self.req.files['file']

        # get the file's hash
        file_hash_ = file_hash(file.stream)
        upl_folder = self.server.config.get_from_pointer('/sys/upload_folder', default='static/files')

        # check if the file exists
        if not os.path.exists(upl_folder):
            os.makedirs(upl_folder)

        # save the file
        file.stream.seek(0)
        file.save(os.path.join(upl_folder, file_hash_))
        return ReturnData(ReturnData.OK).add('sha1', file_hash_).add('size', os.path.getsize(
            os.path.join(upl_folder, file_hash_)))

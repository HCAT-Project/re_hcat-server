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
@File       : upload.py

@Author     : hsn

@Date       : 4/9/23 8:19 AM

@Version    : 1.0.0
"""

from werkzeug.datastructures import FileStorage

from src.containers import ReturnData
from src.event.base_event import BaseEvent
from src.util.file_manager import FileManager


class Upload(BaseEvent):
    auth = True

    def _run(self, file_type='file'):
        _ = self.gettext_func
        # check if the file is in the request
        if 'file' not in self.req.files:
            return ReturnData(ReturnData.NULL, _('No file uploaded.'))

        # get the file
        _file: FileStorage = self.req.files['file']

        assert isinstance(self.server.upload_folder, FileManager)
        file_timeout = self.server.config.get_from_pointer('/network/upload/file_timeout', default=86400)
        if file_type == 'profile_photo':
            file_timeout = 300

        _hash = self.server.upload_folder.save_file(_file.stream, timeout=file_timeout)
        return ReturnData(ReturnData.OK).add('hash', _hash)

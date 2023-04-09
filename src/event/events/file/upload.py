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
import os

from src.containers import ReturnData
from src.event.base_event import BaseEvent


class Upload(BaseEvent):
    auth = True

    def _run(self):
        _ = self.gettext_func
        print(1)
        print(self.req.files)
        if 'file' not in self.req.files:
            return ReturnData(ReturnData.NULL, _('No file uploaded.'))
        file = self.req.files['file']

        file_4096_hash = hashlib.sha1(file.stream.read(4096)).hexdigest()
        upl_folder = self.server.config.get_from_pointer('/sys/upload_folder', default='static/files')

        if not os.path.exists(upl_folder):
            os.makedirs(upl_folder)

        file.stream.seek(0)
        file.save(os.path.join(upl_folder, file_4096_hash))
        #todo:add comments

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
@File       : get_avatar_url.py

@Author     : hsn

@Date       : 7/4/23 8:56 PM

@Version    : 1.0.0
"""
from src.containers import ReturnData
from src.event.base_event import BaseEvent


class GetAvatarUrl(BaseEvent):
    auth = True

    def _run(self, user_id=None, hash_=None):
        _ = self.gettext_func
        # get user data
        if self.server.is_user_exist(user_id):
            user = self.server.get_user(user_id)
            hash_ = user.avatar
        elif not self.server.upload_folder.get_file_path(hash_):
            return ReturnData(ReturnData.ERROR, _('File not found.'))
        return ReturnData(ReturnData.OK).add('url', f'/files/{hash_}')
    #todo:add default avatar

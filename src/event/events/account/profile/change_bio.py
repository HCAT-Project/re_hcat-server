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
@File       : change_bio.py

@Author     : hsn

@Date       : 7/4/23 9:23 PM

@Version    : 1.0.0
"""
import re

from src.containers import ReturnData
from src.event.base_event import BaseEvent
from src.util.regex import bio_regex


class ChangeBio(BaseEvent):
    """
    Change the bio
    Success -> {status: 'ok', message: 'Bio changed successfully.'}
    Error -> {status: 'error', message: 'Bio does not match {} .'}
    """
    auth = True

    def _run(self, bio: str):
        _ = self.gettext_func
        # check if is valid
        if not re.match(bio_regex, bio):
            return ReturnData(ReturnData.ERROR,
                              _('Bio does not match {} .').format(bio_regex))
        # if re.findall(bio_invalid_regex, bio):
        #     return ReturnData(ReturnData.ERROR,
        #                       _('Bio has invalid characters.'))
        with self.server.update_user_data(self.user_id) as user:
            user.bio = bio
        return ReturnData(ReturnData.OK, msg=_('Bio changed successfully.'))

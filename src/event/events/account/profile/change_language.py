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
@File       : change_language.py

@Author     : hsn

@Date       : 8/17/23 9:18 PM

@Version    : 1.0.0
"""
from pathlib import Path

from src.containers import ReturnData
from src.event.base_event import BaseEvent


class ChangeLanguage(BaseEvent):
    """
    Change the language
    Success -> {status: 'ok', message: 'Language changed successfully.'}
    Error -> {status: 'error', message: error message}
    """
    auth = True

    def _run(self, lang: str):
        _ = self.gettext_func
        with self.server.update_user_data(self.user_id) as user:
            if not Path('locale', lang).exists():
                return ReturnData(ReturnData.ERROR,
                                  _('Language not supported.'))
            user.language = lang
        return ReturnData(ReturnData.OK, msg=_('Language changed successfully.'))

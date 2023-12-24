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
@File       : verify.py

@Author     : hsn

@Date       : 12/20/23 8:40 PM
"""
from src.containers import ReturnData
from src.event.base_event import BaseEvent


class Verify(BaseEvent):
    auth = False

    def _run(self, code: str):
        _ = self.gettext_func

        if self.server.config['email']['enable-email-verification']:
            with self.server.update_user_data(self.user_id) as user:
                if user.email is None:
                    return ReturnData(status=ReturnData.ERROR, msg=_('You have not bound an email.'))
                if user.email_verified:
                    return ReturnData(status=ReturnData.ERROR, msg=_('Email has been verified.'))
                try:
                    e = self.server.uem.get_event(code.lower())
                except KeyError:
                    return ReturnData(status=ReturnData.ERROR, msg=_('Invalid code.'))
                if e['user_id'] != self.user_id:
                    return ReturnData(status=ReturnData.ERROR, msg=_('Invalid code.'))
                if e['email'] != user.email:
                    return ReturnData(status=ReturnData.ERROR, msg=_('Invalid code.'))
                if e['event_type'] != 'email_bind':
                    return ReturnData(status=ReturnData.ERROR, msg=_('Invalid code.'))
                user.email_verified = True
                self.server.uem.delete(e['rid'])
                return ReturnData(msg=_('Email verified.'))

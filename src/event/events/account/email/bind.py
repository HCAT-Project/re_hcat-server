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
@File       : bind.py

@Author     : hsn

@Date       : 12/20/23 6:22 PM
"""
import re

from src.containers import ReturnData
from src.event.base_event import BaseEvent
from src.util import send_email
from src.util.regex import regex_email


class Bind(BaseEvent):
    """
    Bind the email
    Bind successful -> {status: 'ok', message: 'Email binding successful.'}
    Bind failed -> {status: 'error', message: error message}
    """
    auth = True

    def _run(self, email: str):
        _ = self.gettext_func

        with self.server.update_user_data(self.user_id) as user:
            if user.email and user.email_verified:
                return ReturnData(ReturnData.ERROR, msg=_('You have bound an email.'))

            if re.fullmatch(regex_email, email) is None:
                return ReturnData(ReturnData.ERROR, msg=_('Invalid email.'))

            try:
                u = self.server.get_user_by_email(email)
                if u.user_name != user.user_name:
                    return ReturnData(ReturnData.ERROR, msg=_('Email has been bound.'))
            except KeyError:
                pass

            user.email = email
            user.email_verified = False

            if self.server.config['email']['enable-email-verification']:
                e = self.server.uem.create_event()
                e.add('user_id', self.user_id)
                e.add('email', email)
                e.add('event_type', 'email_bind')
                e.write_in()

                email_code = e.get_sid()
                mail_host = self.server.config['email']['email-account']['email-host']
                mail_user = self.server.config['email']['email-account']['email-user']
                mail_pass = self.server.config['email']['email-account']['email-password']
                sender = self.server.config['email']['email-account']['email-user']

                content = _('Your verification code is: {} \nValid in 3 minutes, please do not send to anyone.') \
                    .format(email_code.upper())
                subject = _('HCAT Email Binding')
                send_email(mail_host, mail_user, mail_pass, email, subject, content, '@' + self.user_id, sender)
                # print(mail_host, mail_user, mail_pass, email, subject, content, '@' + self.user_id, sender)
            return ReturnData(ReturnData.OK, msg=_('Email binding successful.') + '\n' + _('Please check your email.'))

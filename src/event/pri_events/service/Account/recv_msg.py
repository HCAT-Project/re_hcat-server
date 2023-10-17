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
@File       : recv_msg.py

@Author     : hsn

@Date       : 2023/3/1 下午6:29

@Version    : 1.0.1
"""
import gettext
import logging
import os
import re

from src import util
from src.containers import UserEvent
from src.event.base_event import BaseEventOfSVACRecvMsg
from src.util.regex import regex_email


class RecvMsg(BaseEventOfSVACRecvMsg):
    bot_id: str = '0sAccount'
    bot_name: str = 'Account_BOT'

    def _reg_cmds(self):
        _ = self.gettext_func

        @self.cmd('email')
        def email(cmd):
            if len(cmd) == 0:
                self.send_msg(_('Command') + ':\\n/email bind [email]\\n/email code [code]\\n/email unbind')

            if cmd[0] == 'bind':
                if self.server.config['email']['enable-email-verification']:
                    with self.server.update_user_data(self.user_id) as user:
                        if user.email is not None:
                            self.send_msg(_('You have already bound an email.'))
                            return

                        if re.fullmatch(regex_email, cmd[1]) is None:
                            self.send_msg(_('Invalid email address.'))
                            return

                        if self.server.db_email.exists(cmd[1]):
                            self.send_msg(_('This email has been bound by another user.'))
                            return

                        with self.server.update_user_data(self.user_id) as user:

                            ec = self.server.uem.create_event()
                            ec.add('user_id', self.user_id)
                            ec.add('email', cmd[1])
                            ec.add('event_type', 'email')
                            ec.write_in()
                            sid = ec.get_sid(self.server.event_sid_table)
                            user.add_user_event(ec)

                    if self.server.debug:
                        logging.getLogger('debug').debug(str(sid))

                    mail_host = self.server.config['email']['email-account']['email-host']
                    mail_user = self.server.config['email']['email-account']['email-user']
                    mail_pass = self.server.config['email']['email-account']['email-password']
                    sender = self.server.config['email']['email-account']['email-user']
                    content = _('Your verification code is: {} \nValid in 3 minutes, please do not send to anyone.') \
                        .format(sid.upper())
                    subject = _('HCAT Email Binding')
                    util.send_email(mail_host, mail_user, mail_pass, cmd[1], subject, content, '@' + self.user_id,
                                    sender)
                    self.send_msg(_('Verification code has been sent to email: {}, please check it.').format(cmd[1]))

                else:
                    self.send_msg(_('Email binding is not enabled.'))

            elif cmd[0] == 'unbind':
                if self.server.config['email']['enable-email-verification']:
                    user = self.server.update_user_data(self.user_id)
                    if user.email is not None:
                        self.send_msg(_('You have not bound an email.'))
                        return

                    with self.server.update_user_data(self.user_id) as user:
                        unbinding_email = user.email
                        user.email = None

                    with self.server.db_email.enter_one(unbinding_email) as v:
                        v.data = None

                    self.send_msg(_('Email unbinding successful.'))
                else:
                    self.send_msg(_('Email binding is not enabled.'))

            elif cmd[0] == 'code':
                if self.server.is_user_event_exist(str(cmd[1]).lower()):
                    e = self.server.get_user_event(str(cmd[1]).lower())
                    with self.server.update_user_data(e['user_id']) as user:
                        user.email = e['email']

                    with self.server.db_email.enter_one(e['email']) as v:
                        e_mail: dict = v.data
                        if not isinstance(e_mail, dict):
                            e_mail = {}
                        e_mail['user_id'] = self.user_id
                        v.data = e_mail

                    self.send_msg(_('Email binding successful.'))
                else:
                    self.send_msg(_('Invalid code.'))

        @self.cmd('lang')
        def lang(cmd):
            _ = self.gettext_func
            if len(cmd) == 0:
                self.send_msg(_('Command') + ':\\n/lang set [lang]\\n/lang list')
                return
            if cmd[0] == 'set':
                if cmd[1] in os.listdir('locale'):
                    with self.server.update_user_data(self.user_id) as user:
                        user.language = cmd[1]
                    self.lang = cmd[1]
                    l10n = gettext.translation("all", localedir="locale", languages=[cmd[1]])
                    l10n.install()
                    _ = l10n.gettext
                    self.send_msg(_('Language set successfully.'))
                else:
                    self.send_msg(_('Invalid language.'))

            elif cmd[0] == 'list':
                self.send_msg(_('Available language') + ':\\n' + '\\n'.join(os.listdir('locale')))

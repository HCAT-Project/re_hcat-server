#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：recv_msg.py

@Author     : hsn

@Date       ：2023/3/1 下午6:29

@Version    : 1.0.0
"""
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
from permitronix import PermissionTable, PermissionNode

import util
from containers import EventContainer, User
from event.base_event import BaseEventOfSVACRecvMsg


class RecvMsg(BaseEventOfSVACRecvMsg):
    bot_id = '0sAccount'
    bot_name = 'Account_BOT'

    def _reg_cmds(self):
        @self.cmd('email')
        def email(cmd):
            if len(cmd) == 0:
                self.send_msg('Command:<br>/email bind [email]')

            if cmd[0] == 'bind':
                if self.server.config['email']['enable-email-verification']:
                    table: PermissionTable = self.server.permitronix.get_permission_table(f'user_{self.user_id}')
                    if table.get_permission('email'):
                        self.send_msg('You have already bound an email.')
                    with self.server.open_user(self.user_id) as u:
                        user: User = u.value

                        ec = EventContainer(self.server.db_event)
                        ec.add('user_id', self.user_id)
                        ec.add('email', cmd[1])
                        ec.add('event_type', 'email')
                        ec.write_in()

                        user.add_user_event(ec)

                    mail_host = self.server.config['email']['email-account']['email-host']
                    mail_user = self.server.config['email']['email-account']['email-user']
                    mail_pass = self.server.config['email']['email-account']['email-pass']
                    sender = self.server.config['email']['email-account']['email-user']
                    content = f'Your verification code is: {ec.rid} \nValid in 3 minutes, please do not send to anyone.'
                    subject = 'HCAT Email Binding'
                    util.send_email(mail_host, mail_user, mail_pass, cmd[1], subject, content, '@' + self.user_id,
                                    sender)

            if cmd[0] == 'code':
                if self.server.db_event.exists(cmd[1]):
                    e = self.server.db_event.get(cmd[1])
                    with self.server.open_user(e['user_id']) as u:
                        user: User = u.value
                        user.email = e['email']

                    with self.server.permitronix.enter('user_' + self.user_id) as p:
                        pt: PermissionTable = p.value
                        pt.set_permission(PermissionNode('email'))

                    self.send_msg('Email binding successful.')
                else:
                    self.send_msg('Invalid code.')

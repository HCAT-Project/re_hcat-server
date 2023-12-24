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
import os

from src.event.base_event import BaseEventOfSVACRecvMsg
from src.event.events.account.email.bind import Bind
from src.event.events.account.email.verify import Verify


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
                req = self.req
                req.data = {"email": cmd[1]}
                rt = self.server.e_mgr.create_event(Bind, req=req, path=req.path)
                self.send_msg(rt.json_data['message'])
            # todo: unbind
            # elif cmd[0] == 'unbind':
            #     if self.server.config['email']['enable-email-verification']:
            #         user = self.server.update_user_data(self.user_id)
            #         if user.email is not None:
            #             self.send_msg(_('You have not bound an email.'))
            #             return
            #
            #         with self.server.update_user_data(self.user_id) as user:
            #             unbinding_email = user.email
            #             user.email = None
            #
            #         with self.server.db_email.enter_one(unbinding_email) as v:
            #             v.data = None
            #
            #         self.send_msg(_('Email unbinding successful.'))
            #     else:
            #         self.send_msg(_('Email binding is not enabled.'))

            elif cmd[0] == 'code':
                req = self.req
                req.data = {"code": cmd[1]}
                rt = self.server.e_mgr.create_event(Verify, req=req, path=req.path)
                self.send_msg(rt.json_data['message'])

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

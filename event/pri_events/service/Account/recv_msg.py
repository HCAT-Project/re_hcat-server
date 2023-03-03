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
import util
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
                    util.send_email()

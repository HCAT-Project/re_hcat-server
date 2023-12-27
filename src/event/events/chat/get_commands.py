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
@File       : get_commands.py

@Author     : hsn

@Date       : 8/17/23 9:30 PM

@Version    : 1.0.0
"""
import importlib
import logging

from src.containers import ReturnData
from src.event.base_event import BaseEvent, BaseEventOfSVACRecvMsg


class GetCommands(BaseEvent):
    auth = True
    returns = {'commands': dict}
    def _run(self, bot_id):
        _ = self.gettext_func
        if not (bot_id[0] in [str(i) for i in range(10)] and bot_id[1] == 's'):
            return ReturnData(ReturnData.ERROR, _('Not a service account.'))
        service_id = bot_id[2:].rstrip(' ')

        try:
            event_module = importlib.import_module(f'src.event.pri_events.service.{service_id}.recv_msg')

            event_class = getattr(event_module, 'RecvMsg')

        except ImportError as e:
            if self.server.debug:
                logging.exception(e)
            return ReturnData(ReturnData.ERROR, _('Service not found.'))
        e: BaseEventOfSVACRecvMsg = event_class(None, None, None, None)

        return ReturnData(ReturnData.OK).add('commands', dict(e.get_cmds()))

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：recv_event.py

@Author     : hsn

@Date       ：2023/3/1 下午6:30

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
import importlib
import traceback

from flask import make_response

from event.base_event import BaseEvent


class RecvEvent(BaseEvent):
    auth = False

    def _run(self):
        try:
            # change the str the "UpperCamelCase"
            class_name = ''
            for i in self.path.split("/")[-1].split("_"):
                class_name += i[0].upper() + (i[1:] if len(i) > 0 else '')

            # get the module
            # > "I think it will be very slow. But, i don't want to improve it, because THIS IS PYTHON! " -- hsn
            event_module = importlib.import_module(f'event.events.{self.path.replace("/", ".")}')

            # get the class of the event
            event_class = getattr(event_module, class_name)

        except:
            # print the exc if under debug mode
            if self.server.debug:
                traceback.print_exc()
            return make_response('No Found', 404)
        try:
            return self.e_mgr.create_event(event_class, self.req, self.path)
        except Exception:
            traceback.print_exc()
            return make_response('Internal Server Error', 500)

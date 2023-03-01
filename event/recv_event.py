#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       ：recv_event.py

@Author     : hsn

@Date       ：2023/3/1 下午6:30

@Version    : 1.0.0
"""
#  Copyright 2023. HCAT-Project-Team
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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

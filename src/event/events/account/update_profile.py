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
@File       : update_profile.py

@Author     : hsn

@Date       : 8/17/23 9:41 PM

@Version    : 1.0.0
"""
import copy
import json
import logging

from src.containers import ReturnData
from src.event.base_event import BaseEvent


class UpdateProfile(BaseEvent):
    auth = True

    def _run(self, profile: str | dict):
        _ = self.gettext_func
        if type(profile) == str:
            try:
                profile = json.loads(profile)
            except json.JSONDecodeError:
                return ReturnData(ReturnData.ERROR, _('Illegal profile.'))
        try:
            for k in profile:
                ec = self.server.dol.load_obj_from_group(path=f'account/change_{k}', group='req_events')

                req = copy.deepcopy(self.req)
                req.form.update(profile)
                rt = self.e_mgr.create_event(ec, req, self.path)
                if rt.json_data['status'] != 'ok':
                    return rt

        except Exception as err:
            logging.exception(err)
            return ReturnData(ReturnData.ERROR, str(err))
        return ReturnData(ReturnData.OK)

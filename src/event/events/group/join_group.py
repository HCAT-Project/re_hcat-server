#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : join_group.py

@Author     : hsn

@Date       : 2023/3/1 下午6:28

@Version    : 1.0.0
"""

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
import time

from src.containers import ReturnData
from src.event.base_event import BaseEvent


class JoinGroup(BaseEvent):
    """
    Join group
    Success -> {status: 'ok'}
    Error -> {status: 'error', message: error message}
    """
    auth = True

    def _run(self, group_id:str, add_info:str):
        _ = self.gettext_func
        ec = self.server.uem.create_event()
        ec. \
            add('type', 'group_join_request'). \
            add('rid', ec.rid). \
            add('group_id', group_id). \
            add('user_id', self.user_id). \
            add('add_info', add_info). \
            add('time', time.time())
        ec.write_in()
        agreed_ec = self.server.uem.create_event()
        agreed_ec. \
            add('type', 'group_join_request_agreed'). \
            add('rid', ec.rid). \
            add('group_id', group_id). \
            add('time', time.time())

        with self.server.update_user_data(self.user_id) as user:
            user_name = user.user_name
            if group_id in user.groups_dict:
                return ReturnData(ReturnData.ERROR, _('You\'re already in the group.'))

        try:
            join_success = False
            with self.server.update_group_data(group_id) as group:
                group_name = group.name
                verif_method = group.group_settings['verification_method']
                answer = group.group_settings['answer']
                admin_list = list(group.admin_list) + [group.owner]
                if verif_method == 'fr':
                    agreed_ec.write_in()
                    group.member_dict[self.user_id] = {'nick': user_name}
                    join_success = True
                    return ReturnData(ReturnData.OK)
                elif verif_method == 'aw':
                    if add_info == answer:
                        agreed_ec.write_in()
                        join_success = True
                        group.member_dict[self.user_id] = {'nick': user_name}
                        return ReturnData(ReturnData.OK)
                    else:
                        return ReturnData(ReturnData.ERROR, _('Wrong answer.'))
        finally:  # "finally" has a higher priority than return, so this statement will be executed no matter what.
            if join_success:
                with self.server.update_user_data(self.user_id) as user:
                    user.groups_dict[group_id] = {'remark': group_name, 'time': time.time()}
                    user.add_user_event(agreed_ec)

        if verif_method == 'na':
            return ReturnData(ReturnData.ERROR, _('This group don\'t allow anyone join.'))

        elif verif_method == 'ac':
            for admin_id in admin_list:
                # add to admin todo_list
                with self.server.update_user_data(admin_id) as user:
                    user.add_user_event(ec)
            return ReturnData(ReturnData.OK, _('Awaiting administrator review.'))

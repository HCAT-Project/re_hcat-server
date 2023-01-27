import time
from html import escape

import util
from containers import Group, User, ReturnData
from event.base_event import BaseEvent


class CreateGroup(BaseEvent):
    auth = True

    def _run(self, group_name):
        group_name_ = escape(group_name)
        while True:
            group_id = '0g' + util.get_random_token(5, upper=False)
            if not self.server.db_group.exists(group_id):
                break
        group = Group(group_id)
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            user.groups_dict[group_id] = {'remark': group_name_, 'time': time.time()}
            user_name = user.user_name

        # set group
        group.name = group_name_
        # todo:create group limit
        group.member_dict[self.user_id] = {'nick': user_name,
                                           'time': time.time()}
        group.owner = self.user_id
        with self.server.db_group.enter(group_id) as g:
            g.value = group
        return ReturnData(ReturnData.OK, '').add('group_id', group_id)

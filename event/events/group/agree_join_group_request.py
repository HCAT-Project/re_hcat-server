import time

from containers import User, ReturnData, Group
from event.base_event import BaseEvent


class AgreeJoinGroupRequest(BaseEvent):
    auth = True

    def _run(self, rid):

        if not self.server.db_event.exists(rid):
            return ReturnData(ReturnData.NULL, 'Event does not exist.')

        with self.server.db_event.enter(rid) as e:
            event: dict = e.value
            req_user_id = event['user_id']
            group_id = event['group_id']

        with self.server.open_user(req_user_id) as u:
            user: User = u.value
            req_user_name = user.user_id

        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            group_name = group.name
            if self.user_id not in group.admin_list + [group.owner]:
                return ReturnData(ReturnData.ERROR, 'You are not the admin.')
            group.member_dict[req_user_id] = {'nick': req_user_name}

        with self.server.open_user(req_user_id) as u:
            user: User = u.value
            user.groups_dict[group_id] = {'remark': group_name, 'time': time.time()}
            return ReturnData(ReturnData.OK)

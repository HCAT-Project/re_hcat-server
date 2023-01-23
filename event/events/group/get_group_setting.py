from containers import User, ReturnData, Group
from event.base_event import BaseEvent


class GetGroupSetting(BaseEvent):
    auth = True

    def _run(self, group_id):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if group_id not in user.groups_dict:
                return ReturnData(ReturnData.NULL, 'You are not in the group.')

        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            return ReturnData(ReturnData.OK).add('data', group.group_settings)

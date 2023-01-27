from containers import Group, User, ReturnData
from event.base_event import BaseEvent


class GetName(BaseEvent):
    auth = False

    def _run(self, group_id):
        if not self.server.db_group.exists(group_id):
            return ReturnData(ReturnData.NULL, 'Group does not exist.')
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            group_name = group.name
        remark = group_name

        if self.user_id is not None:
            with self.server.open_user(self.user_id) as u:
                user: User = u.value
                if group_id in user.groups_dict:
                    remark = user.groups_dict[group_id]['remark']

        return ReturnData(ReturnData.OK).add('group_name', group_name).add('remark', remark)

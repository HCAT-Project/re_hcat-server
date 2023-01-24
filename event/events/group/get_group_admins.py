from containers import Group, ReturnData
from event.base_event import BaseEvent


class GetGroupAdmins(BaseEvent):
    auth = True

    def _run(self, group_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if self.user_id in group.member_dict:
                return ReturnData(ReturnData.OK).add('data', list(group.admin_list))
            else:
                return ReturnData(ReturnData.NULL, 'You are not in the group.')

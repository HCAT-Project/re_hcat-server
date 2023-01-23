from containers import Group, ReturnData
from event.base_event import BaseEvent


class Leave(BaseEvent):
    auth = True

    def _run(self, group_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id not in group.member_dict:
                return ReturnData(ReturnData.NULL, 'You are not in the group.')

            if self.user_id == group_id.owner:
                return ReturnData(ReturnData.ERROR, 'You are the group leader, you can not leave the group.')

            if self.user_id in list(group.admin_list):
                group.admin_list.remove(self.user_id)

            group.member_dict.pop(self.user_id)
            return ReturnData(ReturnData.OK)

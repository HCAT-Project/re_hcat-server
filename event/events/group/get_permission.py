from containers import Group, ReturnData
from event.base_event import BaseEvent


class GetPermission(BaseEvent):
    auth = True

    def _run(self, group_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id in group.member_dict:
                if self.user_id == group.owner:
                    rt = 'owner'
                elif self.user_id in group.admin_list:
                    rt = 'admin'
                else:
                    rt = 'member'
                return ReturnData(ReturnData.OK).add('data', rt)
            else:
                return ReturnData(ReturnData.ERROR, 'You are not in the group.')

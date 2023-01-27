from containers import Group, ReturnData
from event.base_event import BaseEvent


class TransferOwnership(BaseEvent):
    auth = True

    def _run(self, group_id, member_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id != group.owner:
                return ReturnData(ReturnData.ERROR, 'You are not the owner.')

            if member_id not in group.member_dict:
                return ReturnData(ReturnData.NULL, f'No member with id:"{member_id}"')

            group.owner = member_id
            group.admin_list.add(self.user_id)
            return ReturnData(ReturnData.OK)

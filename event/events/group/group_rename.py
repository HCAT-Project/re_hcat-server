from containers import Group, ReturnData
from event.base_event import BaseEvent


class GroupRename(BaseEvent):
    auth = True

    def _run(self, group_id, name):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id not in list(group.admin_list) + [group_id.owner]:
                return ReturnData(ReturnData.ERROR, 'You are not the admin.')

            group.name = name
            return ReturnData(ReturnData.OK)

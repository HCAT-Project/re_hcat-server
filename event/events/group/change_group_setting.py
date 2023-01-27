import json

from containers import Group, ReturnData
from event.base_event import BaseEvent


class ChangeGroupSetting(BaseEvent):
    auth = True

    def _run(self, group_id, setting):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id not in list(group.admin_list) + [group_id.owner]:
                return ReturnData(ReturnData.ERROR, 'You don\'t have permission.')

            error_list = list(filter(lambda x: x not in group.group_settings, setting))

            if len(error_list) >= 1:
                return ReturnData(ReturnData.NULL, f'key:"{str(error_list)}" does not exist')
            group.group_settings = {k: (setting[k] if k in setting else group.group_settings[k]) for k in
                                    group.group_settings}
            return ReturnData(ReturnData.OK)

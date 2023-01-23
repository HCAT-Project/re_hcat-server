from containers import ReturnData, Group
from event.base_event import BaseEvent


class GetVerificationMethod(BaseEvent):
    auth = True

    def _run(self, group_id):
        if not self.server.db_group.exists(group_id):
            return ReturnData(ReturnData.NULL, 'Group does not exist.')
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            return ReturnData(ReturnData.OK). \
                add('data',
                    {'verification_method': group.group_settings['verification_method'],
                     'question': group.group_settings['question']})

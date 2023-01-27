from containers import ReturnData, Group
from event.base_event import BaseEvent
from html import escape


class ChangeUserNick(BaseEvent):
    auth = True

    # todo:admin change member nick
    def _run(self, group_id, nick):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id not in group.member_dict:
                return ReturnData(ReturnData.ERROR, 'You are not in the group.')

            group.member_dict['nick'] = escape(nick)

from html import escape

from containers import ReturnData, Group
from event.base_event import BaseEvent


class ChangeUserNick(BaseEvent):
    auth = True

    def _run(self, group_id, nick, user_id=None):
        _user_id = self.user_id if user_id is None else user_id

        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if user_id is not None and self.user_id not in list(group.admin_list) + [group.owner]:
                return ReturnData(ReturnData.ERROR, 'You don\'t have permission.')

            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if _user_id not in group.member_dict:
                return ReturnData(ReturnData.ERROR, 'You are not in the group.')

            group.member_dict[_user_id]['nick'] = escape(nick)

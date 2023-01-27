import time

from containers import Group, ReturnData, User, EventContainer
from event.base_event import BaseEvent


class Kick(BaseEvent):
    auth = True

    def _run(self, group_id, member_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if self.user_id == member_id:
                return ReturnData(ReturnData.ERROR, 'Can\'t kick yourself out.')
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if self.user_id not in list(group.admin_list) + [group.owner]:
                return ReturnData(ReturnData.ERROR, 'You are not the owner.')

            if member_id not in group.member_dict:
                return ReturnData(ReturnData.NULL, f'No member with id:"{member_id}"')

            if member_id in list(group.admin_list):
                group.admin_list.remove(member_id)

            group.member_dict.pop(member_id)
            ec = EventContainer(self.server.db_event)
            ec. \
                add('type', 'admin_removed'). \
                add('rid', ec.rid). \
                add('group_id', group_id). \
                add('time', time.time()). \
                add('member_id', member_id)
            ec.write_in()
            group.broadcast(self.server, None, ec)

        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            user.groups_dict.pop(group_id)

        return ReturnData(ReturnData.OK)

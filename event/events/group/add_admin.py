import time

from containers import Group, ReturnData, EventContainer, User
from event.base_event import BaseEvent


class AddAdmin(BaseEvent):
    auth = True

    def _run(self, group_id, member_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if member_id not in group.member_dict:
                return ReturnData(ReturnData.NULL, f'No member with id:"{member_id}"')

            if self.user_id != group.owner:
                return ReturnData(ReturnData.ERROR, 'You are not the owner.')

            if member_id in group.admin_list or member_id == group.owner:
                return ReturnData(ReturnData.ERROR, 'the member is already an admin')

            group.admin_list.add(member_id)
        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'admin_added'). \
            add('rid', ec.rid). \
            add('group_id', group_id). \
            add('time', time.time()). \
            add('name', member_id)
        ec.write_in()

        for m in group.member_dict:
            with self.server.open_user(m) as u:
                user: User = u.value
                user.add_user_event(ec)

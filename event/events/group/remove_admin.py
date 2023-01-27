import time

from containers import Group, ReturnData, EventContainer, User
from event.base_event import BaseEvent


class RemoveAdmin(BaseEvent):
    auth = True

    def _run(self, group_id, admin_id):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if admin_id not in group.admin_list:
                return ReturnData(ReturnData.NULL, f'No admin with id:"{admin_id}"')

            if self.user_id != group.owner:
                return ReturnData(ReturnData.ERROR, 'You are not the owner.')

            if admin_id == group.owner:
                return ReturnData(ReturnData.ERROR, 'You can\'t make the group owner the admin.')

            group.admin_list.add(admin_id)
        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'admin_removed'). \
            add('rid', ec.rid). \
            add('group_id', group_id). \
            add('time', time.time()). \
            add('name', admin_id)
        ec.write_in()

        for m in group.member_dict:
            with self.server.open_user(m) as u:
                user: User = u.value
                user.add_user_event(ec)
        return ReturnData(ReturnData.OK)

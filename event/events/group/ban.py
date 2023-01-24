import time

from containers import Group, ReturnData, EventContainer, User
from event.base_event import BaseEvent


class Ban(BaseEvent):
    auth = True

    def _run(self, group_id, member_id, ban_time):
        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if group is None:
                return ReturnData(ReturnData.NULL, 'Group does not exist.')

            if (
                    self.user_id not in group.admin_list) or (
                    member_id in group.admin_list and self.user_id != group.owner) or (
                    member_id == group.owner
            ):
                return ReturnData(ReturnData.ERROR, 'You don\'t have permission.')

            try:
                group.ban_dict[self.member_name] = {'time': time.time() + float(ban_time)}
            except:
                return ReturnData(ReturnData.ERROR, 'Wrong data type.')

            ec = EventContainer(self.server.db_event)
            ec. \
                add('type', 'banned'). \
                add('rid', ec.rid). \
                add('group_id', group_id). \
                add('time', time.time()). \
                add('ban_time', ban_time)  # 精确到秒
            ec.write_in()

        with self.server.open_user(member_id) as u:
            user: User = u.value
            user.add_user_event(ec)

        return ReturnData(ReturnData.OK, '')

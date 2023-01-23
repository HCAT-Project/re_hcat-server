import time
from html import escape

from containers import User, ReturnData, EventContainer, Group
from event.base_event import BaseEvent


class SendGroupMsg(BaseEvent):
    auth = True

    def _run(self, group_id, msg):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if group_id not in user.groups_dict:
                return ReturnData(ReturnData.NULL, 'You are not in the group.')

        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'group_msg'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('msg', escape(msg)). \
            add('time', time.time())
        ec.write_in()

        with self.server.db_group(group_id) as g:
            group: Group = g.value
            group.broadcast(self.server, self.user_id, escape(msg))

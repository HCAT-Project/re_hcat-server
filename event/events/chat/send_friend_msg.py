import time

from containers import User, ReturnData, EventContainer
from event.base_event import BaseEvent


class SendFriendMsg(BaseEvent):
    auth = True

    def _run(self, friend_id, msg):
        # {"type":"msg_type","msg":"context"}

        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, 'The person is not your friend.')
        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'friend_msg'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('msg', msg). \
            add('time', time.time())
        ec.write_in()
        with self.server.open_user(friend_id) as u:
            user: User = u.value
            user.add_user_event(ec)

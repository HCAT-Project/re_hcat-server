import time

from containers import ReturnData, User, EventContainer
from event.base_event import BaseEvent


class DeleteFriend(BaseEvent):
    auth = True

    def _run(self, friend_id):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, 'The person is not your friend.')

            user.friend_dict.pop(friend_id)

        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'friend_deleted'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('time', time.time())
        ec.write_in()

        with self.server.open_user(friend_id) as u:
            user: User = u.value
            user.friend_dict.pop(self.user_id)
            user.add_user_event(ec)
            return ReturnData(ReturnData.OK)

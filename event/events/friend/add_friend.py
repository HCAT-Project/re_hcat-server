import time

from containers import ReturnData, User, EventContainer
from event.base_event import BaseEvent


class AddFriend(BaseEvent):
    auth = True

    def _run(self, user_id, add_info):
        if not self.server.is_user_exist(user_id):
            return ReturnData(ReturnData.NULL, 'User does not exist.').jsonify()
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if user_id in user.friend_dict:
                return ReturnData(ReturnData.ERROR, 'You are already friends with each other.')

        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'friend_request'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('req_user_id', user_id). \
            add('add_info', add_info). \
            add('time', time.time())
        ec.write_in()

        with self.server.open_user(user_id) as u:
            user: User = u.value

            user.add_user_event(ec)
            return ReturnData(ReturnData.OK)

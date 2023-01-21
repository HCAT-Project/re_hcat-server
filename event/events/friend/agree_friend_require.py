import time

from containers import ReturnData, User, EventContainer
from event.base_event import BaseEvent


class AgreeFriendRequire(BaseEvent):
    auth = True

    def _run(self, rid):
        agree_time = time.time()

        with self.server.db_event.enter(rid) as v:
            if v.value is None:
                return ReturnData(ReturnData.NULL, 'This event does not exist.')
            event: dict = v.value

        if event['req_user_id'] != self.user_id:
            return ReturnData(ReturnData.ERROR, 'The person did not send you a friend request.')

        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if event['user_id'] in user.friend_dict:
                return ReturnData(ReturnData.ERROR, 'You are already friends with each other.')
            user.friend_dict[event['user_id']] = {'nick': event['user_id'], 'time': agree_time}

        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'friend_agree'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('time', time.time())
        ec.write_in()

        with self.server.open_user(event['user_id']) as u:
            user: User = u.value
            user.friend_dict[self.user_id] = {'nick': self.user_id, 'time': agree_time}
            user.add_user_event(ec)
        return ReturnData(ReturnData.OK)

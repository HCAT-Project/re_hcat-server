from containers import User, ReturnData
from event.base_event import BaseEvent


class GetFriendNick(BaseEvent):
    auth = True

    def _run(self, friend_id):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, 'The person is not your friend.')
            if 'nick' not in user.friend_dict[friend_id]:
                user.friend_dict[friend_id]['nick'] = friend_id
            return ReturnData(ReturnData.OK).add('nick', user.friend_dict[friend_id]['nick'])

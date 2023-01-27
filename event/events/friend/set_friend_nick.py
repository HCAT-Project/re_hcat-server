from containers import ReturnData, User
from event.base_event import BaseEvent
from html import escape

class SetFriendNick(BaseEvent):
    auth = True

    def _run(self, friend_id, nick):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, 'The person is not your friend.')
            user.friend_dict[friend_id]['nick'] = escape(nick)
            return ReturnData(ReturnData.OK)

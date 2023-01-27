from containers import ReturnData, User
from event.base_event import BaseEvent


class GetFriendList(BaseEvent):
    auth = True

    def _run(self):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            return ReturnData(ReturnData.OK).add('data', [i for i in user.friend_dict])

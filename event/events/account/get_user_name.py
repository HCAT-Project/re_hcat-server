from containers import User, ReturnData
from event.base_event import BaseEvent


class GetUserName(BaseEvent):
    auth = False

    def _run(self, user_id):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            nick = None
            if user_id in user.friend_dict:
                nick = user.friend_dict[user_id]['nick']

        if self.server.is_user_exist(user_id):
            with self.server.open_user(user_id) as u:
                user: User = u.value
                rt = ReturnData(ReturnData.OK).add('data', user.user_name)
                if nick:
                    rt.add('nick', nick)
                return rt
        else:
            return ReturnData(ReturnData.NULL, 'User does not exist.').jsonify()

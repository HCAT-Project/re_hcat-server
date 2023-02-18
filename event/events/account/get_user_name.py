import importlib

from containers import User, ReturnData
from event.base_event import BaseEvent


class GetUserName(BaseEvent):
    auth = False

    def _run(self, user_id: str):
        if user_id[0] in [str(i) for i in range(10)] and user_id[1] == 's':
            service_id = user_id[2:].rstrip(' ')
            name = importlib.import_module( f'event.pri_events.service.{service_id}.__init__').name
            rt = ReturnData(ReturnData.OK).add('data', name).add('nick', name)
            return rt

        # get nick if logged in
        nick = None
        if self.user_id is not None:
            with self.server.open_user(self.user_id) as u:
                user: User = u.value
                if user_id in user.friend_dict:
                    nick = user.friend_dict[user_id]['nick']

        # get username
        if self.server.is_user_exist(user_id):
            with self.server.open_user(user_id) as u:
                user: User = u.value
                rt = ReturnData(ReturnData.OK).add('data', user.user_name)
                if nick is not None:
                    rt.add('nick', nick)
                return rt
        else:
            return ReturnData(ReturnData.NULL, 'User does not exist.').jsonify()

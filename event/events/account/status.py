from containers import ReturnData, User
from event.base_event import BaseEvent


class Status(BaseEvent):
    auth = False

    def _run(self, user_id):
        if user_id[0] in [str(i) for i in range(10)] and user_id[1] == 's':
            return ReturnData(ReturnData.OK).add('status', 'online')
        if not self.server.is_user_exist(user_id):
            return ReturnData(ReturnData.NULL, 'User does not exist.')
        with self.server.open_user(user_id) as u:
            user: User = u.value
            return ReturnData(ReturnData.OK).add('status', str(user.status))

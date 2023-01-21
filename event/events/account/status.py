from containers import ReturnData, User
from event.base_event import BaseEvent


class Status(BaseEvent):
    auth = False

    def _run(self, user_id):
        if not self.server.is_user_exist(user_id):
            return ReturnData(ReturnData.NULL, 'User does not exist.')
        with self.server.open_user(user_id) as u:
            user: User = u.value
            return ReturnData(ReturnData.OK).add('status', str(user.status))

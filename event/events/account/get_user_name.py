from containers import User, ReturnData
from event.base_event import BaseEvent


class GetUserName(BaseEvent):
    auth = False

    def _run(self, user_id):
        if self.server.is_user_exist(user_id):
            with self.server.open_user(user_id) as u:
                user: User = u.value
                return ReturnData(ReturnData.OK).add('data', user.user_name)
        else:
            return ReturnData(ReturnData.NULL, 'User does not exist.')

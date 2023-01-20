import util
from containers import User, ReturnData
from event.base_event import BaseEvent


class Logout(BaseEvent):
    auth = True

    def _run(self):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            user.token = util.get_random_token(256)
        return ReturnData(ReturnData.OK)

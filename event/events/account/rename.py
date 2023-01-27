from containers import User, ReturnData
from event.base_event import BaseEvent
from html import escape

class Rename(BaseEvent):
    auth = True

    def _run(self, name):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            user.user_name = escape(name)
            return ReturnData(ReturnData.OK)

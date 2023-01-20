from containers import User, ReturnData
from event.base_event import BaseEvent


class GetTodoList(BaseEvent):
    auth = True

    def _run(self):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            rt = ReturnData(ReturnData.OK).add('data', user.todo_list)
            user.todo_list = []
            return rt

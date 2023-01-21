from containers import User, ReturnData
from event.base_event import BaseEvent


class GetTodoList(BaseEvent):
    auth = True

    def _run(self):
        self.server.activity_dict_lock.acquire()
        self.server.activity_dict[self.user_id] = 30
        self.server.activity_dict_lock.release()
        
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            user.status = 'online'
            rt = ReturnData(ReturnData.OK).add('data', user.todo_list)
            user.todo_list = []
            return rt

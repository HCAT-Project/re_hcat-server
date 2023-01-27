from containers import User, ReturnData
from event.base_event import BaseEvent


class GetGroupsList(BaseEvent):
    """
    Deprecated!

    Please use 'get_groups'
    """
    auth = True

    def _run(self):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            return ReturnData(ReturnData.OK).add('data', list(user.groups_dict))

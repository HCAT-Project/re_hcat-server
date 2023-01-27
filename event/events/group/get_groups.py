from containers import User, ReturnData
from event.base_event import BaseEvent


class GetGroups(BaseEvent):
    auth = True

    def _run(self):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            return ReturnData(ReturnData.OK).add('data', {i:{'remark':user.groups_dict[i]['remark']} for i in list(user.groups_dict)})

from containers import User, ReturnData
from event.base_event import BaseEvent


class ChangeRemark(BaseEvent):
    auth = True

    def _run(self, group_id, remark):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if group_id not in user.groups_dict:
                return ReturnData(ReturnData.ERROR, 'You are not in the group.')
            user.groups_dict[group_id]['remark'] = remark

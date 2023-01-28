from containers import ReturnData, User
from event.base_event import BaseEvent


class ChangePassword(BaseEvent):
    auth = True

    def _run(self, password):
        # check if the password is longer than 6 digits
        if len(password) < 6:
            return ReturnData(ReturnData.ERROR, 'Password is too short.')
        # get user and change password
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            user.change_password(password)
            return ReturnData(ReturnData.OK)

import re
from html import escape

from containers import ReturnData, User
from event.base_event import BaseEvent


class Register(BaseEvent):
    auth = False

    def _run(self, user_id, password, username):
        if self.server.is_user_exist(user_id):
            return ReturnData(ReturnData.ERROR, 'ID has been registered.').jsonify()

        # check if user_id is legal
        reg = r'^[a-zA-Z][a-zA-Z0-9_]{4,15}$'
        if not re.match(reg, user_id):
            return ReturnData(ReturnData.ERROR,
                              f'User ID does not match {reg} .').jsonify()

        # check if the password is longer than 6 digits
        if len(password) < 6:
            return ReturnData(ReturnData.ERROR, 'Password is too short.')

        with self.server.open_user(user_id) as u:
            u.value = User(user_id, password, escape(username))
            return ReturnData(ReturnData.OK)

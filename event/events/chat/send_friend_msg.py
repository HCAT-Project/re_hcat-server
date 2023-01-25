import time

from containers import User, ReturnData, EventContainer
from event.base_event import BaseEvent
from html import escape


class SendFriendMsg(BaseEvent):
    auth = True

    def _run(self, friend_id, msg):
        # {"msg_chain":[{"type":type,"msg":msg},{"type":type,"msg":msg}]}

        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, 'The person is not your friend.')

        if 'msg_chain' not in msg or len(msg['msg_chain']):
            return ReturnData(ReturnData.ERROR, 'Illegal messages.')


        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'friend_msg'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('msg', escape(msg)). \
            add('time', time.time())
        ec.write_in()
        with self.server.open_user(friend_id) as u:
            user: User = u.value
            user.add_user_event(ec)
            return ReturnData(ReturnData.OK)

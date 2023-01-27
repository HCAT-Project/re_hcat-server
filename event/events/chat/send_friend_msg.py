import copy
import json
import time
from html import escape

from containers import User, ReturnData, EventContainer
from event.base_event import BaseEvent


class SendFriendMsg(BaseEvent):
    auth = True

    def _run(self, friend_id, msg):
        # {"msg_chain":[{"type":type,"msg":msg},{"type":type,"msg":msg}]}
        msg_ = copy.copy(msg)
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, 'The person is not your friend.')

        try:
            if type(msg_) == str:
                msg_ = json.loads(msg_)
            if len(msg_['msg_chain']) == 0:
                raise
            for i in range(len(msg_['msg_chain'])):
                if msg_['msg_chain'][i]['type'] == 'text':
                    msg_['msg_chain'][i]['msg'] = escape(msg_['msg_chain'][i]['msg'])

        except:
            return ReturnData(ReturnData.ERROR, 'Illegal messages.')

        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'friend_msg'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('msg', msg_). \
            add('time', time.time())
        ec.write_in()
        with self.server.open_user(friend_id) as u:
            user: User = u.value
            user.add_user_event(ec)
            return ReturnData(ReturnData.OK)

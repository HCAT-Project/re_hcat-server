import copy
import time

import util
from containers import User, ReturnData, EventContainer
from event.base_event import BaseEvent
from event.pri_events.service.recv_sv_account_msg import RecvSvAccountMsg


class SendFriendMsg(BaseEvent):
    auth = True

    def _run(self, friend_id, msg):
        # {"msg_chain":[{"type":type,"msg":msg},{"type":type,"msg":msg}]}
        msg_ = copy.copy(msg)
        if len(friend_id) <= 1:
            return ReturnData(ReturnData.NULL, 'The person is not your friend.')

        # check if the msg is service Account
        if friend_id[0] in [str(i) for i in range(10)] and friend_id[1] == 's':
            return self.e_mgr.create_event(RecvSvAccountMsg, self.req, self.path)
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if friend_id not in user.friend_dict:
                return ReturnData(ReturnData.NULL, 'The person is not your friend.')

        try:
            msg_ = util.msg_process(msg_)
        except:
            return ReturnData(ReturnData.ERROR, 'Illegal messages.')

        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            name = user.user_name

        with self.server.open_user(friend_id) as u:
            user: User = u.value
            nick = user.friend_dict[self.user_id]['nick']
            ec = EventContainer(self.server.db_event)
            ec. \
                add('type', 'friend_msg'). \
                add('rid', ec.rid). \
                add('user_id', self.user_id). \
                add('friend_id', self.user_id). \
                add('friend_nick', nick). \
                add('friend_name', name). \
                add('msg', msg_). \
                add('_WARNING', 'user_id is deprecated!!!'). \
                add('time', time.time())
            ec.write_in()
            user.add_user_event(ec)
            return ReturnData(ReturnData.OK)

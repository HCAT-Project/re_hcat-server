import copy

from event.base_event import BaseEvent
from event.events.chat.send_friend_msg import SendFriendMsg
from event.pri_events.service.recv_sv_account_msg import RecvSvAccountMsg


class SvMsg(BaseEvent):
    auth = True
    main_event = SendFriendMsg

    def _run(self, friend_id, msg):
        msg_ = copy.copy(msg)
        # check if the msg is service Account
        if friend_id[0] in [str(i) for i in range(10)] and friend_id[1] == 's':
            return True, self.e_mgr.create_event(RecvSvAccountMsg, self.req, self.path)

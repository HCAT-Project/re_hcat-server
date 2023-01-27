from event.base_event import BaseEvent
from send_group_msg import SendGroupMsg
from send_friend_msg import SendFriendMsg


class SendMsg(BaseEvent):
    auth = True

    def _run(self, target_id: str, msg):
        if target_id.startswith('0g'):
            return self.e_mgr.create_event(SendGroupMsg, self.req, self.path)
        else:
            return self.e_mgr.create_event(SendFriendMsg, self.req, self.path)

from event.base_event import BaseEvent


class RecvSvAccountMsg(BaseEvent):
    auth = True

    def _run(self, friend_id, msg):
        ...

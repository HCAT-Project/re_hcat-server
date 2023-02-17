from event.base_event import BaseEvent


class RecvMsg(BaseEvent):
    auth = True

    def _run(self, msg: str):
        ...

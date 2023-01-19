from event.base_event import BaseEvent


class TestEvent(BaseEvent):
    auth = False
    requirements = []
    def _run(self, *args):
        print(1)
from event.base_event import BaseEvent


class TestEvent(BaseEvent):
    auth = False
    requirements = ['test']

    def _run(self, test):
        print(test)

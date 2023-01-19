from flask import make_response

from event.base_event import BaseEvent
import importlib


class RecvEvent(BaseEvent):
    auth = False
    requirements = []

    def _run(self):
        try:
            class_name = ''
            for i in self.path.split("/")[-1].split("_"):
                class_name += i[0].upper() + (i[1:] if len(i) > 0 else '')

            event_module = importlib.import_module(f'event.events.{self.path.replace("/", ".")}')
            return self.e_mgr.create_event(getattr(event_module, class_name), self.req, self.path)
        except:
            return make_response('No Found', 404)

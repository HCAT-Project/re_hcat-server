import importlib
import traceback

from flask import make_response

from event.base_event import BaseEvent


class RecvEvent(BaseEvent):
    auth = False

    def _run(self):
        try:
            class_name = ''
            for i in self.path.split("/")[-1].split("_"):
                class_name += i[0].upper() + (i[1:] if len(i) > 0 else '')

            event_module = importlib.import_module(f'event.events.{self.path.replace("/", ".")}')
            event_class = getattr(event_module, class_name)

        except:
            if self.server.debug:
                traceback.print_exc()
            return make_response('No Found', 404)
        try:
            return self.e_mgr.create_event(event_class, self.req, self.path)
        except Exception:
            traceback.print_exc()
            return make_response('Internal Server Error', 500)

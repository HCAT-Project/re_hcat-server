import inspect
import json

from werkzeug.local import LocalProxy

import util
from containers import ReturnData
from event.event_manager import EventManager


class BaseEvent:
    auth = True

    def __init__(self, server, req, path: str, e_mgr: EventManager):
        self.req = req
        self.server = server
        self.path = path
        self.e_mgr = e_mgr

    def run(self):
        req_data = util.request_parse(self.req)
        requirements = [i for i in inspect.signature(self._run).parameters]
        if util.ins(requirements, req_data):
            if len(requirements) > 0:
                return self._run(*[req_data[k] for k in requirements])
            else:
                return self._run()
        else:
            return ReturnData(ReturnData.ERROR,
                              f'Parameters do not meet the requirements:[{",".join(requirements)}]').jsonify()

    def _run(self, *args):
        ...

import json

from werkzeug.local import LocalProxy

import util
from containers import ReturnData
from event.event_manager import EventManager


class BaseEvent:
    auth = True
    requirements = []

    def __init__(self, server, req, path: str, e_mgr:EventManager):
        self.req = req
        self.server = server
        self.path = path
        self.e_mgr=e_mgr

    def run(self):
        req_data = util.request_parse(self.req)

        if util.ins(self.requirements, req_data):
            if len(self.requirements) > 0:
                return self._run([req_data[k] for k in self.requirements])
            else:
                return self._run()
        else:
            return ReturnData(ReturnData.ERROR,
                              f'Parameters do not meet the requirements:[{",".join(self.requirements)}]').json()

    def _run(self, *args):
        ...

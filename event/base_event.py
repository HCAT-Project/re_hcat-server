import inspect
import json

from werkzeug.local import LocalProxy

import util
from containers import ReturnData
from event.event_manager import EventManager


class BaseEvent:
    auth = True

    def __init__(self, server, req, path: str, e_mgr: EventManager, user_id=None):
        self.req = req
        self.server = server
        self.path = path
        self.e_mgr = e_mgr
        self.user_id = user_id

    def run(self):
        req_data = util.request_parse(self.req)
        params = inspect.signature(self._run).parameters
        requirements = [i for i in params]
        m_requirements = list(filter(lambda x: str(params[x].default) == '<class \'inspect._empty\'>', requirements))
        if util.ins(m_requirements, req_data):
            if len(requirements) > 0:
                return self._run(*[req_data[k] for k in requirements])
            else:
                return self._run()
        else:
            return ReturnData(ReturnData.ERROR,
                              f'Parameters do not meet the requirements:[{",".join(filter(lambda x: x not in req_data, m_requirements))}]').jsonify()

    def _run(self, *args):
        ...

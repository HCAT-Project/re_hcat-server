import json
import logging

from containers import ReturnData, User
from util import AesCrypto


class EventManager:
    def __init__(self, server):
        self.server = server
        self.logger = logging.getLogger(__name__)
        self.auxiliary_events = {}

    def add_auxiliary_event(self, main_event: type, event: type):
        if main_event not in self.auxiliary_events:
            self.auxiliary_events[main_event] = []
        self.auxiliary_events[main_event].append(event)

    def create_event(self, event, req, path):
        auth_success = False
        j = {'user_id': None}

        # run auxiliary events
        ae_rt = None
        cancel = False
        if event in self.auxiliary_events:
            for e in self.auxiliary_events[event]:
                ae_rt_temp = self.create_event(e, req, path)
                if ae_rt_temp is not None:
                    if not isinstance(ae_rt_temp,tuple) or len(ae_rt_temp) == 1:
                        if isinstance(ae_rt_temp, bool):
                            ae_rt_temp = (ae_rt_temp, ReturnData(ReturnData.NULL, '').jsonify())
                        else:
                            ae_rt_temp = (False, ae_rt_temp)

                    if ae_rt_temp[1] != ReturnData(ReturnData.NULL, '').jsonify():
                        ae_rt = ae_rt_temp[1]
                    cancel = ae_rt_temp[0] or cancel

        if 'auth_data' in req.cookies:
            auth_data = req.cookies['auth_data']
            try:
                auth_data_decrypto = AesCrypto(self.server.key).decrypt(auth_data)
                j = json.loads(auth_data_decrypto)
                with self.server.open_user(j['user_id']) as v:
                    user: User = v.value
                    auth_success = user.auth_token(j['token'])
            except:
                if event.auth:
                    return ReturnData(ReturnData.ERROR, 'Invalid token.').jsonify()

        if not event.auth:
            auth_success = True
        if auth_success:
            if not cancel:
                e = event(self.server, req, path, self, j['user_id'])
                rt = e.run()
                if type(rt) == ReturnData:
                    rt = rt.jsonify()
                return rt if rt is not None else (
                    ae_rt if ae_rt is not None else ReturnData(ReturnData.NULL, '').jsonify())
            else:
                return ae_rt if ae_rt is not None else ReturnData(ReturnData.NULL, '').jsonify()
        else:
            return ReturnData(ReturnData.ERROR, 'Invalid token.').jsonify()

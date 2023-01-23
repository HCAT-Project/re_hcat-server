import json
import logging

from containers import ReturnData, User
from util import AesCrypto


class EventManager:
    def __init__(self, server):
        self.server = server
        self.logger = logging.getLogger(__name__)

    def create_event(self, event, req, path):
        auth_success = False
        j = {'user_id': None}

        if 'auth_data' in req.cookies:
            auth_data = req.cookies['auth_data']
            try:
                auth_data_decrypto = AesCrypto(self.server.key).decrypto(auth_data)
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
            e = event(self.server, req, path, self, j['user_id'])
            rt = e.run()
            if type(rt) == ReturnData:
                rt = rt.jsonify()
            return rt if rt is not None else ReturnData(ReturnData.NULL, '').jsonify()
        else:
            return ReturnData(ReturnData.ERROR, 'Invalid token.').jsonify()

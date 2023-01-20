import json

from containers import ReturnData, User
from util import AesCrypto


class EventManager:
    def __init__(self, server):
        self.server = server

    def create_event(self, event, req, path):
        auth_success = True
        if event.auth:
            auth_success = False
            if 'auth_data' in req.cookies:
                auth_data = req.cookies['auth_data']
                auth_data_decrypto = AesCrypto(self.server.key).decrypto(auth_data)
                j = json.loads(auth_data_decrypto)
                with self.server.open_user(j['user_id']) as v:
                    user: User = v.value
                    auth_success = user.auth_token(j['token'])
        if auth_success:
            e = event(self.server, req, path, self)
            rt = e.run()
            return rt if rt is not None else ReturnData(ReturnData.OK, '').jsonify()
        else:
            return ReturnData(ReturnData.ERROR, 'Invalid token.').jsonify()

import json

from containers import ReturnData
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
                auth_success = self.server.auth_token(j['user_id'], j['token'])
        if auth_success:
            e = event(self.server, req, path,self)
            rt=e.run()
            return rt if rt is not None else ReturnData(ReturnData.OK, '').json()
        else:
            return ReturnData(ReturnData.ERROR, 'Invalid token.').json()

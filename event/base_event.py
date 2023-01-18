import json

from werkzeug.local import LocalProxy

from server import Server
from util import AesCrypto


class BaseEvent:
    auth=True
    def __init__(self):
        ...
    def run(self,server:Server,req:LocalProxy):
        if self.auth:
            auth_success==False
            if 'auth_data' in req.cookies:
                auth_data=req.cookies['auth_data']
                auth_data_decrypto=AesCrypto(server.key).decrypto(auth_data)
                j=json.loads(auth_data_decrypto)


        self._run()
    def _run(self):

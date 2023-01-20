from containers import ReturnData
from event.base_event import BaseEvent


class AuthenticateToken(BaseEvent):
    auth = True

    def _run(self):
        return ReturnData(ReturnData.OK).jsonify()

from containers import ReturnData
from event.base_event import BaseEvent


class GetVer(BaseEvent):
    auth = False

    def _run(self):
        return ReturnData(ReturnData.OK, self.server.ver)

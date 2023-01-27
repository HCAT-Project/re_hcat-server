import copy
import json
import time
from html import escape

from containers import User, ReturnData, EventContainer, Group
from event.base_event import BaseEvent


class SendGroupMsg(BaseEvent):
    auth = True

    def _run(self, group_id, msg):
        msg_ = copy.copy(msg)
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            if group_id not in user.groups_dict:
                return ReturnData(ReturnData.NULL, 'You are not in the group.')

        try:
            if type(msg_) == str:
                msg_ = json.loads(msg_)
            if len(msg_['msg_chain']) == 0:
                raise
            for i in range(len(msg_['msg_chain'])):
                if msg_['msg_chain'][i]['type'] == 'text':
                    msg_['msg_chain'][i]['msg'] = escape(msg_['msg_chain'][i]['msg'])

        except:
            return ReturnData(ReturnData.ERROR, 'Illegal messages.')

        ec = EventContainer(self.server.db_event)
        ec. \
            add('type', 'group_msg'). \
            add('rid', ec.rid). \
            add('user_id', self.user_id). \
            add('msg', msg_). \
            add('time', time.time())

        with self.server.db_group.enter(group_id) as g:
            group: Group = g.value
            if self.user_id in group.ban_dict:
                if group.ban_dict[self.user_id]['time'] < time.time():
                    del group.ban_dict[self.user_id]
                else:
                    return ReturnData(ReturnData.ERROR, 'You have been banned by admin.')
            group.broadcast(self.server, self.user_id, msg_)
            ec.write_in()

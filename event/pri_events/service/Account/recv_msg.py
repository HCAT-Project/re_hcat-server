from containers import User, ReturnData
from event.base_event import BaseEvent
from util.command_parser import Command


class RecvMsg(BaseEvent):
    auth = True

    def _run(self, msg: str):
        with self.server.open_user(self.user_id) as u:
            user: User = u.value
            try:
                print(0)
                cmd = Command(msg)
                if cmd[0] == 'help':
                    user.add_fri_msg2todos(self.server, '0sAccount', 'Account_BOT', 'Account_BOT',
                                           """
                                           Commands:
                                           /help: this msg.
                                           """)
                else:
                    user.add_fri_msg2todos(self.server, '0sAccount', 'Account_BOT', 'Account_BOT',
                                           "Sorry,i can't understand.")
            except:
                print(1)
                user.add_fri_msg2todos(self.server, '0sAccount', 'Account_BOT', 'Account_BOT',
                                       'Hello, please use `/help` for help.')
            return ReturnData(ReturnData.OK)

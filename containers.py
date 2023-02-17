import time

from RPDB.database import RPDB
from flask import jsonify

import util
from util.jelly import Jelly

from server import Server
from util import get_random_token


class EventContainer:
    def __init__(self, data_base: RPDB):
        self.data_base = data_base
        while True:
            rid = get_random_token(8)
            if not self.data_base.exists(rid):
                break
        self.rid = rid
        self.json = {}
        self.can_write = True
        self. \
            add('rid', self.rid). \
            add('time', time.time())

    def __call__(self, key, value):
        self.json[key] = value

    def write_in(self):
        with self.data_base.enter(self.rid) as v:
            v.value = self.json

    def add(self, key, value):
        self.json[key] = value
        return self


class ReturnData:
    ERROR = 1
    NULL = 2
    OK = 0

    def __init__(self, status=0, msg=''):
        if status == 0:
            status_text = 'ok'
        elif status == 1:
            status_text = 'error'
        elif status == 2:
            status_text = 'null'
        else:
            status_text = 'error'
        self.json_data = {'status': status_text, 'message': msg}

    def add(self, key, value):
        self.json_data[key] = value
        return self

    def jsonify(self):
        return jsonify(self.json_data)

    def __call__(self):
        return self.json_data


class User(Jelly):
    def __init__(self, user_id, password, user_name):
        super().__init__()
        self.hash_password = None
        self.salt = None
        self.user_id = user_id
        self.user_name = user_name
        self.change_password(password)

    def _var_init(self):
        self.todo_list = []
        self.token = ''
        self.status = 'offline'
        self.friend_dict = {}
        self.groups_dict = {}
        self.e_mail_auth = False  # todo:邮箱认证

    def change_password(self, password):
        """
        :param password:
        :return:
        """
        self.salt = util.get_random_token(16)
        self.hash_password = util.salted_hash(password, self.salt, self.user_id)

    def auth(self, password: str) -> bool:
        """
        :param password:
        :return:
        """
        return util.salted_hash(password, self.salt, self.user_id) == self.hash_password

    def is_in_group(self, server, group_id: str) -> bool:
        """
        :param server: server obj
        :param group_id:
        :return: bool
        """
        db = server.db_group
        if not db.exists(group_id):
            return False

        if group_id in self.groups_dict and self.user_id in db.get(group_id).member_dict:
            return True

        return False

    def add_user_event(self, ec: EventContainer):
        """

        :param ec: EventContainer
        :return:
        """
        self.todo_list.append(ec.json)

    def auth_token(self, token) -> bool:
        """
        :param token:
        :return:
        """
        return self.token == token


class Group(Jelly):
    Permission_OWNER = 0
    Permission_ADMIN = 1

    def __init__(self, group_id):
        super().__init__()
        self.id = group_id

    def _var_init(self):
        self.name = ''
        self.member_dict = {}
        self.owner = ''
        self.admin_list = set()
        self.member_settings = {}
        self.ban_dict = {}
        '''
        verification_method:
        ac:administrator consent--需要管理同意
        fr:free--自由进出
        aw:answer question--需要回答问题
        na:not allowed--不允许加入
        '''
        self.group_settings = {'verification_method': 'ac', 'question': '', 'answer': ''}

    def broadcast(self, server, user_id: str, ec: EventContainer):
        """
        :param server: server obj
        :param user_id:
        :param ec:
        :return:
        """
        for i in filter(lambda j: j != user_id, list(self.member_dict)):
            # add to member's todo_list
            with server.open_user(i) as u:
                user: User = u.value
                user.add_user_event(ec)

    def permission_match(self, user_id: str, permission=Permission_ADMIN) -> bool:
        """
        :param user_id: str
        :param permission: Group.Permission_ADMIN or Group.Permission_OWNER
        :return: bool
        """
        if permission == self.Permission_ADMIN:
            return user_id == self.owner or user_id in self.admin_list
        elif permission == self.Permission_OWNER:
            return user_id == self.owner

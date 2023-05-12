#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : __init__.py

@Author     : hsn

@Date       : 2023/3/1 下午6:30

@Version    : 1.0.0
"""

#  Copyright (C) 2023. HCAT-Project-Team
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
import base64
import copy
import hashlib
import json
import logging
import random
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from typing import Iterable, Any

import pyaes
from flask import Request


class AesCrypto:
    def __init__(self, key: str, mode=pyaes.aes.AESModeOfOperationECB):
        """
        Initializes an AES encryption object with the given key and mode.
        :param key: The encryption key, should be between 16 and 32 bytes long and an integer multiple of 4 bytes.
        :param mode: The encryption mode, defaults to ECB.
        """
        self.mode = mode
        if 16 <= len(key) <= 32 and len(key) % 4 == 0:
            self.key = key
        else:
            raise ValueError(
                'The AES key length should be greater than 16 bytes and less than 32 bytes and be an integer multiple '
                'of 4 bytes.')
        self.aes = self.mode(self.key.encode('utf8'))

    def encrypt(self, data: str):
        """
        Encrypts the given data using the AES object's key and mode.
        :param data: The data to be encrypted.
        :return: The base64-encoded encrypted result.
        """
        data_bytes = data.encode('utf8')
        data_bytes += bytes([0] * (16 - (len(data_bytes) % 16)))
        rt_bytes = bytes([])
        for i in range(int(len(data_bytes) / 16)):
            rt_bytes += self.aes.encrypt(data_bytes[16 * i:16 * (i + 1)])
        return base64.b64encode(rt_bytes).decode('utf8')

    def decrypt(self, cipher_text: str):
        """
        Decrypts the given base64-encoded cipher text using the AES object's key and mode.
        :param cipher_text: The base64-encoded cipher text to be decrypted.
        :return: The decrypted data as a string.
        """
        data_bytes = base64.b64decode(cipher_text)
        rt_bytes = bytes([])
        for i in range(int(len(data_bytes) / 16)):
            rt_bytes += self.aes.decrypt(data_bytes[16 * i:16 * (i + 1)])
        return rt_bytes.rstrip(b'\x00').decode('utf8')


def salted_sha256(data, salt, additional_string=None):
    """
    Generates a salted hash for the given data and salt.
    :param data: The data to be hashed.
    :param salt: The salt to use for the hash.
    :param additional_string: An additional string to add to the hash if desired.
    :return: The salted hash as a hexadecimal string.
    """
    hash_salt = salt
    if additional_string is not None:
        hash_salt += hashlib.sha256(additional_string.encode('utf8')).hexdigest()
    return hashlib.sha256((data + hash_salt).encode('utf8')).hexdigest()


def salted_sha1(data, salt, additional_string=None):
    """
    Generates a salted hash for the given data and salt.
    :param data: The data to be hashed.
    :param salt: The salt to use for the hash.
    :param additional_string: An additional string to add to the hash if desired.
    :return: The salted hash as a hexadecimal string.
    """
    hash_salt = salt
    if additional_string is not None:
        hash_salt += hashlib.sha1(additional_string.encode('utf8'),usedforsecurity=False).hexdigest()
    return hashlib.sha1((data + hash_salt).encode('utf8'),usedforsecurity=False).hexdigest()


def get_random_token(key_len=128, upper=True):
    """
    Generates a random token of the specified length.
    :param key_len: The length of the token to be generated.
    :param upper: If True, include uppercase letters in the token. Otherwise, only use lowercase and digits.
    :return: The generated token as a string.
    """
    if upper:
        choices = list(range(65, 91)) + list(range(97, 123)) + list(range(48, 58))
    else:
        choices = list(range(97, 123)) + list(range(48, 58))
    return ''.join([chr(random.choice(choices)) for _ in range(key_len)])


def ins(obj: Iterable, collection: Iterable) -> bool:
    """
    Checks if all elements in an iterable are in another iterable.

    :param obj: Iterable to check.
    :param collection: Iterable to check against.
    :return: True if all elements in obj are in collection, False otherwise.
    """
    return all(elem in collection for elem in obj)


def not_ins(obj: Iterable, collection: Iterable) -> bool:
    """
    Checks if all elements in an iterable are not in another iterable.

    :param obj: Iterable to check.
    :param collection: Iterable to check against.
    :return: True if all elements in obj are not in collection, False otherwise.
    """
    return all(elem not in collection for elem in obj)


def request_parse(req_data: Request) -> dict:
    """
    Parses the data from a request.

    :param req_data: ImmutableMultiDict representing the data in the request.
    :return: A dictionary containing the data in the request.
    """
    if req_data.method == 'POST':
        data = dict(req_data.form)
    elif req_data.method == 'GET':
        data_dict = {}
        for key, value in req_data.args.items():
            data_dict[key] = value
        data = data_dict
    else:
        data = {}
    return data


def msg_process(msg: Any) -> dict:
    """
    Processes a message, escaping text messages and raising an error if the message chain is empty.

    :param msg: The message to process.
    :return: The processed message as a dictionary.
    """
    msg_ = copy.copy(msg)
    if isinstance(msg_, str):
        msg_ = json.loads(msg_)
    if len(msg_['msg_chain']) == 0:
        raise ValueError("Message chain is empty.")

    for i in range(len(msg_['msg_chain'])):
        if msg_['msg_chain'][i]['type'] == 'text':
            if len(msg_['msg_chain'][i]['msg']) == 0:
                raise ValueError("Element in message chain is empty.")
            msg_['msg_chain'][i]['msg'] = msg_['msg_chain'][i]['msg']

    # todo:add comments
    # todo:file process
    return msg_


def send_email(mail_host, mail_user, mail_password, receiver_address, subject='', content='', receiver='', sender=''):
    receivers = [receiver_address]

    message = MIMEText(content, 'plain', 'utf-8') if isinstance(content, str) else content
    message['From'] = Header(sender, 'utf-8')
    message['To'] = Header(receiver, 'utf-8')

    message['Subject'] = Header(subject, 'utf-8')

    smtp_obj = smtplib.SMTP()
    smtp_obj.connect(mail_host, 25)
    smtp_obj.login(mail_user, mail_password)
    smtp_obj.sendmail(mail_user, receivers, message.as_string())


def decorators_with_parameters(func):
    def wrapper(*args, **kwargs):
        def wrapper2(func_):
            return func(func_, *args, **kwargs)

        return wrapper2

    return wrapper


def multi_line_log(logger: logging.Logger = logging.getLogger(), level: int = logging.INFO, msg: str = ""):
    for line in msg.splitlines():
        logger.log(level, line)


def under_score_to_pascal_case(name):
    return ''.join([x.capitalize() for x in name.split('_')])

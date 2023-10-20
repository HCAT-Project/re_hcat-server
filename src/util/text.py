#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Copyright (C) 2023. HCAT-Project-Team
#  _
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  _
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  _
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
@File       : text.py

@Author     : hsn

@Date       : 5/17/23 7:19 PM

@Version    : 1.0.1
"""
import copy
import json
import secrets
import string
from typing import Any


def under_score_to_pascal_case(name: str) -> str:
    """
    Converts a string from under_score to PascalCase.
    :param name: The string to convert.
    :return: The converted string.
    """
    return ''.join([x.capitalize() for x in name.split('_')])


def pascal_case_to_under_score(name) -> str:
    """
    Converts a string from PascalCase to under_score.
    :param name: The string to convert.
    :return: The converted string.
    """

    def temp():
        for i, t in enumerate(name):
            if t.isupper() and i != 0:
                yield from "_" + t.lower()
            else:
                yield t.lower()

    return ''.join(temp())


def msg_process(msg: Any) -> dict:
    """
    Processes a message, escaping text messages and raising an error if the message chain is empty.

    :param msg: The message to process.
    :return: The processed message as a dictionary.
    """
    msg_ = copy.copy(msg)
    if isinstance(msg_, str):
        try:
            msg_ = json.loads(msg_)
        except json.decoder.JSONDecodeError:
            msg_ = {'msg_chain': [{'type': 'text', 'msg': msg_}]}
    if len(msg_['msg_chain']) == 0:
        raise ValueError("Message chain is empty.")
    # Check if the type is legal
    _check_msg_type(msg_)

    # Check if the reply is in the top of the message chain
    _check_msg_reply(msg_)

    # Check if the message is legal
    _check_if_msg_is_legal(msg_)

    # todo:add comments
    # todo:file process
    return msg_


def _check_if_msg_is_legal(msg_):
    for i, msg_e in enumerate(msg_['msg_chain']):
        if msg_e['type'] == 'text':
            if len(msg_e['msg']) == 0:
                raise ValueError("Element in message chain is empty.")
            elif len(msg_e['msg']) > 500:
                raise ValueError("Element in message chain is too long.")

        elif msg_e['type'] in ['img', 'file', 'voice', 'sticker']:
            if len(msg_e['msg']) != 40:
                raise ValueError("Img hash is illegal.")


def _check_msg_reply(msg_):
    _temp_end = False
    for i, msg_e in enumerate(msg_['msg_chain']):
        if msg_e['type'] == 'reply':
            if _temp_end:
                raise ValueError("Reply is not in the top of the message chain.")
        else:
            _temp_end = True


def _check_msg_type(msg_):
    for i in msg_['msg_chain']:
        if i['type'] not in ['text', 'img', 'file', 'sticker', 'at', 'reply', 'voice']:
            raise ValueError("Illegal type in message chain.")


def random_str(_len: int = 128, upper: bool = True) -> str:
    """
    Generates a random string of the specified length.
    :param _len: The length of the string to be generated.
    :param upper: Whether to include uppercase letters in the string.
    :return:
    """

    if upper:
        choices = string.ascii_letters + string.digits
    else:
        choices = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(choices) for _ in range(_len))

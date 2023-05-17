#!/usr/bin/env python
# -*- coding: UTF-8 -*-

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

"""
@File       : text.py

@Author     : hsn

@Date       : 5/17/23 7:19 PM

@Version    : 1.0.0
"""
import copy
import json
from typing import Any


def under_score_to_pascal_case(name):
    return ''.join([x.capitalize() for x in name.split('_')])


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



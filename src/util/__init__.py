#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File       : __init__.py

@Author     : hsn

@Date       : 2023/3/1 下午6:30

@Version    : 1.0.0
"""
import json
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
import logging
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from typing import Iterable, Callable

from flask import Request


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
    if req_data.method == "POST":
        try:
            data = json.loads(req_data.data)
        except json.JSONDecodeError:
            data = {}
    elif req_data.method == "GET":
        data_dict = {}
        for key, value in req_data.args.items():
            data_dict[key] = value
        data = data_dict
    else:
        data = {}
    return data


def send_email(
        mail_host,
        mail_user,
        mail_password,
        receiver_address,
        subject="",
        content="",
        receiver="",
        sender="",
):
    receivers = [receiver_address]

    message = (
        MIMEText(content, "plain", "utf-8") if isinstance(content, str) else content
    )
    message["From"] = Header(sender, "utf-8")
    message["To"] = Header(receiver, "utf-8")

    message["Subject"] = Header(subject, "utf-8")

    smtp_obj = smtplib.SMTP()
    smtp_obj.connect(mail_host, 25)
    smtp_obj.login(mail_user, mail_password)
    smtp_obj.sendmail(mail_user, receivers, message.as_string())


def multi_line_log(
        logger: logging.Logger = logging.getLogger(),
        level: int = logging.INFO,
        msg: str = "",
):
    for line in msg.splitlines():
        logger.log(level, line)


class AutoValidateDescriptor:
    def __init__(self, name: str, func_set: Callable, err: BaseException = Exception()):
        self.name = name
        self.func_set = func_set
        self.err = err

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if self.func_set and not self.func_set(instance, value):
            if self.err:
                raise self.err
            else:
                raise ValueError(f"{self.name} is not valid.")

        instance.__dict__[self.name] = value

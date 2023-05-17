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
@File       : crypto.py

@Author     : hsn

@Date       : 5/17/23 7:22 PM

@Version    : 1.0.0
"""
import base64
import hashlib
import io
import secrets
import string
import tempfile
from os import PathLike
from typing import Union, IO

import pyaes


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
        hash_salt += hashlib.sha1(additional_string.encode('utf8'), usedforsecurity=False).hexdigest()
    return hashlib.sha1((data + hash_salt).encode('utf8'), usedforsecurity=False).hexdigest()


def get_random_token(key_len=128, upper=True):
    """
    Generates a random token of the specified length.
    :param key_len: The length of the token to be generated.
    :param upper: If True, include uppercase letters in the token. Otherwise, only use lowercase and digits.
    :return: The generated token as a string.
    """
    if upper:
        choices = string.ascii_letters + string.digits
    else:
        choices = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(choices) for _ in range(key_len))


def read_chunks(file: Union[str, PathLike, IO[bytes]], chunk_size: int = io.DEFAULT_BUFFER_SIZE):
    if isinstance(file, (str, PathLike)):
        f = open(file, 'rb')
    elif isinstance(file, (IO, tempfile.SpooledTemporaryFile, _io.BufferedReader)):
        f = file
    else:
        raise TypeError(f'Unsupported type {type(file)}')

    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield chunk


def file_hash(file: Union[str, PathLike, IO[bytes]] = None, hasher=None):
    if file is None:
        raise ValueError("File cannot be None")
    h = hasher() if hasher is not None else hashlib.sha1(usedforsecurity=False)
    for chunk in read_chunks(file):
        h.update(chunk)
    return h.hexdigest()

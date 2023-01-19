import base64
import hashlib
import random

import pyaes


class AesCrypto:
    def __init__(self, key: str, mode=pyaes.aes.AESModeOfOperationECB):
        self.mode = mode
        if 16 <= len(key) <= 32 and len(key) % 4 == 0:
            self.key = key
        else:
            raise ValueError(
                'The AES key length should be greater than 16 bytes and less than 32 bytes and be an integer multiple of 4 bytes.')
        self.aes = self.mode(self.key.encode('utf8'))

    def encrypto(self, data: str):
        data_bytes = data.encode('utf8')  # 编码
        data_bytes += bytes([0] * (16 - (len(data_bytes) % 16)))  # 补位
        rt_bytes = bytes([])
        for i in range(int(len(data_bytes) / 16)):
            rt_bytes += self.aes.encrypt(data_bytes[16 * i:16 * (i + 1)])
        return base64.b64encode(rt_bytes).decode('utf8')

    def decrypto(self, cipher_text: str):
        data_bytes = base64.b64decode(cipher_text)
        rt_bytes = bytes([])
        for i in range(int(len(data_bytes) / 16)):
            rt_bytes += self.aes.decrypt(data_bytes[16 * i:16 * (i + 1)])
        return rt_bytes.rstrip(b'\x00').decode('utf8')


def salted_hash(data, salt, additional_string=None):
    hash_salt = salt
    if additional_string is not None:
        hash_salt += hashlib.sha1(additional_string.encode('utf8')).hexdigest()
    return hashlib.sha1((data + hash_salt).encode('utf8')).hexdigest()


def get_random_token(key_len=128):
    return ''.join(
        [chr(random.choice(list(range(65, 91)) + list(range(97, 123)) + list(range(48, 58)))) for _ in range(key_len)])


def ins(obj: iter, collection) -> bool:
    res = True
    for i in obj:
        res = res and (i in collection)
    return res


def not_ins(obj: iter, collection) -> bool:
    res = True
    for i in obj:
        res = res and (i not in collection)
    return res


def request_parse(req_data):
    if req_data.method == 'POST':
        data = dict(req_data.form)
    elif req_data.method == 'GET':
        data_dict = {}
        for i in req_data.args.items():
            data_dict[i[0]] = i[1]
        data = data_dict
    else:
        data = {}
    return data

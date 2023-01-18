import base64
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


def get_random_token(key_len=128):
    return ''.join(
        [chr(random.choice(list(range(65, 91)) + list(range(97, 123)) + list(range(48, 58)))) for _ in range(key_len)])

from ..conf import parser

import jwt

import time
from typing import Optional, Dict

option = parser.options("token")
print("[syncJwt] is imported.")


class Component:

    def __init__(self):
        self.over_time = int(option["over_time"])
        self.secret = option["secret"]
        self.algorithm = option["algorithm"]

    def __enter__(self):
        return self

    def decode(self, payload: str or bytes) -> Dict:
        """

        解析jwt加密的token，如果无法解析抛出异常

        :param payload: 需要解析的负载
        :return: dict

        """
        return jwt.decode(payload, self.secret, algorithm=self.algorithm)

    def encode(self, payload: dict, exp: Optional[int] = None) -> bytes:
        """

        编码dict对象成为jwt二进制对象，当做token使用

        :param payload: 需要加密的dict对象
        :param exp: 有效时间
        :return: str

        """
        payload["exp"] = int(time.time()) + (exp or self.over_time)
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

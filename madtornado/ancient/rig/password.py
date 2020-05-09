from hmac import HMAC
from os import urandom
from hashlib import sha256
from binascii import b2a_base64, a2b_base64


def encrypt(password: str, salt: bytes = None) -> bytes:
    """

    密码加密

    :param password: 密码值
    :param salt: salt值，默认不用填写
    :return: 加密后的密码，无法逆向解析

    """
    if salt is None:
        salt = urandom(8)
    assert 8 == len(salt), "salt length is not 8"
    if isinstance(salt, str):
        salt = salt.encode('UTF-8')
    if isinstance(password, str):
        password = password.encode('UTF-8')
    for i in range(10):
        password = HMAC(password, salt, sha256).digest()
    return b2a_base64(salt + password)


def validate(hashed: str, input_password: str) -> bool:
    """

    密码验证

    :param hashed: 加密的密码
    :param input_password: 需要比对的密码
    :return: bool

    """
    salt_original = a2b_base64(hashed)
    if isinstance(hashed, str):
        hashed = hashed.encode('UTF-8')
    return hashed == encrypt(input_password, salt=salt_original[:8])

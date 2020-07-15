from hmac import HMAC
from os import urandom
from hashlib import sha256
from binascii import b2a_base64, a2b_base64


def iso7064mod11_2(source: str) -> str:
    """

    iso7064mod11-2校验算法

    :param source: 需要添加校验的字符串
    :return: 校验位

    """
    sigma = 0
    size = len(source)
    index = 0
    for i in source:
        weight = (2 ** (size - index)) % 11
        sigma += (ord(i) - 48) * weight
        index += 1
    sigma %= 11
    sigma = ((12 - sigma) % 11)
    return "X" if sigma == 10 else chr(48 + sigma)


def iso7064mod37_2(source: str) -> str:
    """

    iso7064mod37_2校验算法

    :param source: 需要添加校验的字符串
    :return: 校验位

    """
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ*"
    sigma = 0
    index = 0
    size = len(source)
    for i in source:
        weight = (2 ** (size - index)) % 37
        sigma += (ord(i) - 48) * weight
        index += 1
    sigma %= 37
    sigma = ((38 - sigma) % 37)
    return alphabet[sigma]


def iso7064mod37_hybrid_36(source: str) -> str:
    """

    iso7064mod37_HYBRID_36校验算法

    :param source: 需要添加校验的字符串
    :return: 校验位

    """
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ*"
    m1 = 36
    m2 = 37

    p = m1
    n = len(source) + 1

    i = n
    while i >= 2:
        s = p + alphabet.index(source[n - i].upper())
        if s % m1 == 0:
            c = m1
        else:
            c = s % m1
        p = (c * 2) % m2
        i -= 1
    return alphabet[(m1 + 1 - p % m1) % m1]


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

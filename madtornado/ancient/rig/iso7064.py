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

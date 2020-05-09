def require(path):
    """

    有时你可能只是需要从文件中读取到json数据，这是require函数将根据
    获取到的path，返回dict对象，相当方便

    :param path:
    :return: dict

    """
    import json
    fp = open(path, "r")
    data = fp.read()
    fp.close()
    try:
        return json.loads(data)
    except json.decoder.JSONDecodeError:
        return {}


def loop(loop_iter):
    """

    导入一个可迭代对象，loop将循环遍历它，通过next()取出下一个内容，
    有时你可能需要循环变换一个状态例如从0-1再从0-1你可能需要loop，
    这个函数类似轮播图，播放到结尾再从头播放

    与itertools.cycle函数效果一致

    :param loop_iter: 可迭代对象
    :return: generator

    """
    flag = 0
    end = len(loop_iter) - 1
    while True:
        if flag > end:
            flag = 0
        yield loop_iter[flag]
        flag += 1


def assign(*args):
    """

    与js中Object.assign表现形式一样

    将所有可枚举属性的值从一个或多个源对象复制到目标对象

    与dict.update(dict)效果一致

    :param args: 复数的dict对象
    :return: 合并后的dict对象

    """
    new_dict = {}
    for d in args:
        new_dict.update(d)
    return new_dict


def grunt(cup, water):
    """

    grunt将cup中的dict对象作为最终产物，用water中的数据进行替换，
    如果water未提供cup中相对应key值的字段，将使用cup中提供的默认内容

    :param cup: 需要的数据dict
    :param water: 源数据dict
    :return: 最终产生的dict

    """
    for item in cup:
        val = water.get(item, None)
        if val is None or val == "":
            ...
        else:
            cup[item] = val
    return cup


def deque(iterable=(), maxlen=None):
    """

    deque返回deque对象，该对象包含的元素恒定，当你添加一个元素时最上层的元素会被销毁

    :param iterable:
    :param maxlen:
    :return:

    """
    import collections
    return collections.deque(iterable=iterable, maxlen=maxlen)


def rang_split(content: str, index: int) -> list:
    """

    根据提供的索引位置分割字符串

    举例::

        abcdefg  index=2
        return ["ab","cdefg"]

    :param content: 字符串
    :param index: 索引位置
    :return: 截取后的列表

    """
    return [content[:index], content[index:]]


def scoop(obj: dict, which: list) -> dict:
    """

    从字典中获取which中指定的内容，如果不存在则捞取的值为None

    :param obj: 源字典
    :param which: 需要获取哪些值
    :return: 捞取后的字典

    """
    new_dict = {}
    for key in which:
        new_dict[key] = obj.get(key, None)
    return new_dict


def plunder(obj: dict, which: list) -> dict:
    """

    从字典中获取which中指定的内容，如果不存在或值不为真不获取该值

    :param obj: 源字典
    :param which: 需要获取哪些值
    :return: 捞取后的字典

    """
    new_dict = {}
    for key in which:
        val = obj.get(key, None)
        if val:
            new_dict[key] = val
    return new_dict

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


class UpdateList(list):
    """

    主要方法update()，该方法是对list类型拓展，
    当update的数据对象存在时对其更新，注意请保证UpdateList
    的子项是dict类型而不要使用值类型，值类型对于UpdateList毫无意义

    """

    def __init__(self, *args, **kwargs):
        super(UpdateList, self).__init__(*args, **kwargs)

        # 对象key值，可以是函数，函数接收val, key返回布尔值代表满足条件
        self.key = None
        # 当key设置为函数时必须定义的回调，传入item对象返回该对象key值内容
        self.on_fetch_key = None
        # 当元素是更新时调用的更新方法，如果元素是插入时不调用，如果不定义该回调默认直接替换
        self.on_update = None
        # 当元素update方法触发的是添加时调用的回调函数，可以自定义append类型
        self.on_append = None

    def __getitem__(self, key):
        if isinstance(self.key, str):
            return self.find(lambda val: val[self.key] == key)
        elif hasattr(self.key, "__call__"):
            return self.find(lambda val: self.key(val, key))
        else:
            return super(UpdateList, self).__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(self.key, str):
            key = self.find(lambda val: val[self.key] == key)[0]
        elif hasattr(self.key, "__call__"):
            key = self.find(lambda val: self.key(val, key))[0]
        super(UpdateList, self).__setitem__(key, value)

    def update(self, p_object):
        """

        类似于append方法，不同的是当内容存在时会对内容进行更新，更新逻辑遵从update_callback
        而当内容不存在时与append方法一致进行末尾加入内容

        :param p_object: 内容对象
        :return: None

        """
        if not self.on_update:
            raise TypeError("Function `on_update` is not defined")

        old_val = None
        if isinstance(self.key, str):
            key = p_object.get(self.key) or -1
            if key != -1:
                key, old_val = self.find(lambda val: val[self.key] == key)
        elif hasattr(self.key, "__call__"):
            try:
                key, old_val = self.find(lambda val: self.key(val, self.on_fetch_key(p_object)))
            except TypeError:
                raise TypeError("Function `on_fetch_key` is not defined")
        else:
            raise TypeError("`key` is not defined")

        if key == -1:
            if self.on_append:
                self.append(self.on_append(p_object))
            else:
                self.append(p_object)
        else:
            super(UpdateList, self).__setitem__(key, self.on_update(old_val, p_object))

    def find(self, callback):
        """

        返回满足回调函数的内容

        :param callback: 回调函数，返回布尔类型用于判断是否满足要求
        :return: (索引，值)

        """
        for index, item in enumerate(self):
            if callback(item):
                return index, item
        return -1, None


def rectangular_factor(x0, y0, x1, y1):
    """

    根据左上角和右下角坐标返回的Rectangular对象

    :return: Rectangular

    """
    return Rectangular(x0, y0, x1 - x1, y1 - y0)


class Rectangular:

    def __init__(self, x, y, w, h):
        """

        矩形对象，不考虑矩阵变换矩形

        :param x: 左上角x坐标点
        :param y: 左上角y坐标点
        :param w: 矩形宽度
        :param h: 矩形高度

        """
        self.x0 = x
        self.y0 = y
        self.x1 = x + w
        self.y1 = y + h
        self.w = w
        self.h = h

    def __gt__(self, other):
        if self.w > other.w and self.h > other.h:
            return True
        return False

    def __lt__(self, other):
        if self.w < other.w and self.h < other.h:
            return True
        return False

    def collision(self, r2):
        """

        判断两个矩形是否产生碰撞关系

        r1.x0 < r2.x1
        r1.y0 < r2.y1
        r1.x1 > r2.x0
        r1.y1 > r2.y0

        :param r2: Rectangular
        :return: 布尔

        """
        if self.x0 < r2.x1 and self.y0 < r2.y1 and self.x1 > r2.x0 and self.y1 > r2.y0:
            return True
        return False

    def contain(self, r2):
        """

        判断矩形中是否包含另外一个矩形r2，注意包含也是矩形碰撞所以collision方法会返回True

        r1.x0 < r2.x0
        r1.x1 > r2.x1
        r1.y0 < r2.y0
        r1.y1 > r2.y1

        :param r2: Rectangular
        :return: 布尔

        """
        if self.x0 < r2.x0 and self.x1 > r2.x1 and self.y0 < r2.y0 and self.y1 > r2.y1:
            return True
        return False

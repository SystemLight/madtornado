from typing import List, Optional, Callable, TypeVar
import os
import platform


def require(path, encoding="utf-8"):
    """

    有时你可能只是需要从文件中读取到json数据，这是require函数将根据
    获取到的path，返回dict对象，相当方便，该函数同样类似于json.load

    :param path:
    :return: dict

    """
    import json
    fp = open(path, "r", encoding=encoding)
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


def find(iterable, func):
    """

    查找可迭代对象的指定项，匹配第一个子项并返回，无匹配项时返回(-1,None)

    :param func: 匹配函数
    :param iterable: 可迭代对象
    :return: 索引，子对象

    """
    for i, v in enumerate(iterable):
        if func(v):
            return i, v
    return -1, None


class UpdateList(list):
    """

    主要方法update()，该方法是对list类型拓展，
    当update的数据对象存在时对其更新，注意请保证UpdateList
    的子项是dict类型而不要使用值类型，值类型对于UpdateList毫无意义

    on_update hook函数，接收old_val(旧数据), p_object(新数据)，需要返回更新数据
    on_append hook函数，接收p_object(添加数据)，需要返回添加数据
    on_fetch_key hook函数，当key属性定义为函数时需要同时定义如何捕获key值

    key 支持字符串，字符串指定子元素中的更新参考值
        支持函数，接收val(当前数据)，key(参考key值)该key值由on_fetch_key返回，函数返回bool值True为更新，False为添加

    on_fetch_key作用::

        复杂场景下我们可能需要up[("home2", True)]这样来找到响应的item，这样显示传递key值没有什么问题，key函数可以获取到
        相应的key数据以供我们处理，但是当我们调用update时，update需要判断该内容是更新还是添加，这时我们传入的内容是数据，显然
        update无法知晓如何获取我们想要的类型key值，如("home2", True)，所以我们要定义on_fetch_key来告知update如何捕获我们
        想要的类型的key值，on_fetch_key只有当key属性定义为函数时才有意义。

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
            self.on_update = lambda o, p: p

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
            raise TypeError("`key` is TypeError")

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
    return Rectangular(x0, y0, x1 - x0, y1 - y0)


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


def retry(freq=3, retry_callback=None):
    """

    装饰器，为函数添加此装饰器当函数抛出异常时会对函数重新调用，重新调用次数取决于freq指定的参数

    :param freq: 重试次数
    :param retry_callback: 重试时回调执行的函数
    :return: 原函数返回值

    """

    def decorator(func):
        def wrap(*args, **kwargs):
            now_freq = 1
            while True:
                try:
                    result = func(*args, **kwargs)
                    break
                except Exception as e:
                    if now_freq > freq:
                        raise e
                    now_freq += 1
                    if hasattr(retry_callback, "__call__"):
                        retry_callback(now_freq)

            return result

        return wrap

    return decorator


def read(path, encoding="utf-8"):
    """

    快捷读取文件函数

    :param path: 文件路径
    :param encoding:
    :return: 读取的文件内容

    """
    with open(path, "r", encoding=encoding) as fp:
        result = fp.read()
    return result


def write(path, data, encoding="utf-8"):
    """

    快捷写入文件函数

    :param path: 文件路径
    :param data: 写入数据
    :param encoding:
    :return: None

    """
    with open(path, "w", encoding=encoding) as fp:
        fp.write(data)


T = TypeVar("T")
ParseCallable = Callable[["TreeOperate", List[T], int], T]


class TreeOperate:
    """

    TreeOperate允许你操作一颗树型结构数据，支持数据导入和导出，数据必须含有key唯一标识，
    子元素必须存储在children键值下
    示例内容::
        _data = {
            "key": "1",
            "title": "root",
            "children": [
                {"key": "2", "title": "2", "children": [
                    {"key": "4", "title": "4"},
                    {"key": "5", "title": "5"}
                ]},
                {"key": "3", "title": "3", "children": [
                    {"key": "6", "title": "6"},
                    {"key": "7", "title": "7"}
                ]}
            ]
        }
        tree_root = TreeOperate.from_dict(_data)
        tree_root.find("2").append(TreeOperate.from_dict({"key": "8", "title": "8"}))
        print(tree_root.find("8"))
        tree_root.find("8").remove()
        print(tree_root.find("8"))

    """

    def __init__(self, key=None):
        self.key = key
        self.pid = None
        self.data = {}
        self.parent = None  # type: Optional[TreeOperate]
        self.__children = []  # type: List[TreeOperate]

    def __str__(self):
        return str({
            "key": self.key,
            "pid": self.pid,
            "data": self.data,
            "children": self.__children
        })

    @staticmethod
    def from_dict(data):
        """

        从dict对象中返回TreeOperate对象
        :param data: dict
        :return: TreeOperate

        """
        tree = TreeOperate(data.get("key", None))
        for d in data:
            if d not in ["key", "children"]:
                tree.data[d] = data[d]
        for i in data.get("children", []):
            tree.append(TreeOperate.from_dict(i))
        return tree

    @staticmethod
    def from_file(path):
        """

        从json文件中读取数据

        :param path: json文件路径
        :return: TreeOperate

        """
        return TreeOperate.from_dict(require(path))

    @property
    def children(self):
        return self.__children

    def append(self, sub_tree: "TreeOperate"):
        """

        为当前节点添加子节点，节点类型必须是TreeOperate类型
        :param sub_tree: 子类型节点
        :return: None

        """
        if not isinstance(sub_tree, TreeOperate):
            raise TypeError("sub_tree must be of type TreeOperate")
        sub_tree.pid = self.key
        sub_tree.parent = self
        self.__children.append(sub_tree)

    def find(self, key: str):
        """

        根据key值查找节点
        :param key: key值
        :return: TreeOperate

        """
        if self.key == key:
            return self
        else:
            for i in self.__children:
                result = i.find(key)
                if result:
                    return result
        return None

    def remove(self, key=None):
        """

        删除节点，如果传递key值，将删除当前节点下匹配的子孙节点，
        如果不传递key值将当前节点从父节点中删除
        :param key: [可选] key值
        :return:

        """
        if key is None:
            if self.parent is not None:
                self.parent.__children.remove(self)
        else:
            remove_child = self.find(key)
            if remove_child:
                remove_child.parent.__children.remove(remove_child)

    def parse(self, callback: ParseCallable, deep=0):
        """

        遍历定制解析规则，返回解析内容

        :param callback: Callable[["TreeOperate", List[T], int], T] 解析回调函数返回解析结果
        :param deep: 当前解析深度，默认不需要填写，用于回调函数接收判断所在层级
        :return: 解析结果

        """
        child_parse_list = []
        for i in self.__children:
            child_parse_list.append(i.parse(callback, deep + 1))
        return callback(self, child_parse_list, deep)

    def count(self):
        """

        统计树型结构节点数量

        :return: 节点数量

        """
        total = 0

        def ct(_a, _b, _c):
            nonlocal total
            total += 1

        self.parse(ct)
        return total

    def to_dict(self, flat=False):
        """

        输出dict类型数据，用于json化
        :param flat: 是否将data参数内容直接映射到对象
        :return: dict

        """
        result = dict(key=self.key, pid=self.pid)
        if flat:
            for j in self.data:
                result[j] = self.data[j]
        else:
            result["data"] = self.data
        children = []
        for i in self.__children:
            children.append(i.to_dict(flat))
        result["children"] = children
        return result


def kill_form_port(port):
    """

    传入端口号，杀死进程

    :param port: 端口号，int类型
    :return: None

    """
    port = str(port)
    if platform.system() == 'Windows':
        command = """for /f "tokens=5" %i in ('netstat -ano ^| find \"""" + port + """\" ') do (taskkill /f /pid %i)"""
    else:
        command = """kill -9 $(netstat -nlp | grep :""" + port + """ | awk '{print $7}' | awk -F "/" '{print $1}')"""
    os.system(command)


def inin(content, pool):
    """

    查找指定内容是否存在于列表的字符串中，这种情况content一定要比列表中字符串短

    举例::

        inin("a",["asdf","fsfsdf"]) 将返回 "asdf"

    :param content: 内容
    :param pool: 列表
    :return: 匹配内容

    """
    for p in pool:
        if content in p:
            return p
    return None


def rinin(content, pool):
    """

    查找指定内容是否存在于列表的字符串中，这种情况content一定要比列表中字符串长

    举例::

        inin("asdf",["a","fsfsdf"]) 将返回 "a"

    :param content: 内容
    :param pool: 列表
    :return: 匹配内容

    """
    for p in pool:
        if p in content:
            return p
    return None

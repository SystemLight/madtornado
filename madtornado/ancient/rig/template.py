from tornado.template import Template, Loader

import os
import re


class GenerateCodeEngine:
    """

    生成代码引擎类

    使用方法::

        gec = GenerateCodeEngine()
        gec.catch_write("index.html", "template.html", {
            "anthor": "systemlight"
        })

    """

    def __init__(self, template_root_path=""):
        """

        构造函数

        :param template_root_path: 模板根目录

        """
        self.glob_content = {}
        self.template_root_path = template_root_path

        self.__start_match_tag = r"//start_user_code"
        self.__end_match_tag = r"//end_user_code"
        self.catch_match = r"{}(.*?){}".format(self.__start_match_tag, self.__end_match_tag)

    @property
    def start_match_tag(self):
        return self.__start_match_tag

    @start_match_tag.setter
    def start_match_tag(self, value):
        self.__start_match_tag = value
        self.catch_match = r"{}(.*?){}".format(self.__start_match_tag, self.__end_match_tag)

    @property
    def end_match_tag(self):
        return self.__end_match_tag

    @end_match_tag.setter
    def end_match_tag(self, value):
        self.__end_match_tag = value
        self.catch_match = r"{}(.*?){}".format(self.__start_match_tag, self.__end_match_tag)

    def register_glob_content(self, name, value):
        """

        注册全局方法或者变量，每个模板渲染时都将附带该内容

        :param name: 名称
        :param value: 内容
        :return: None

        """
        self.glob_content[name] = value

    def render(self, template_path, kwargs=None):
        """

        根据模板渲染并生成字符串返回

        :param template_path: 模板文件路径
        :param kwargs: 包含写入模板中的变量数据和函数等
        :return: 渲染后的内容

        """
        template_path = os.path.join(self.template_root_path, template_path)
        if kwargs is None:
            kwargs = {}
        with open(template_path, "r", encoding="utf-8") as fp:
            temp = Template(fp.read(), autoescape=None, loader=Loader(self.template_root_path))
        glob_content = {**self.glob_content, **kwargs}
        return temp.generate(**glob_content)

    def write(self, path, template_path, kwargs=None):
        """

        将渲染内容希尔到文件当中

        :param path: 目标文件路径
        :param template_path: 模板文件路径
        :param kwargs: 包含写入模板中的变量数据和函数等
        :return: None

        """
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(self.render(template_path, kwargs).decode())

    def catch_write(self, path, template_path, kwargs=None):
        """

        捕获用户代码写入方法，执行写入之前会先匹配用户代码

        :param path: 目标文件路径
        :param template_path: 模板文件路径
        :param kwargs: 其它额外参数，参考catch_user_code方法，包含写入模板中的变量数据和函数等
        :return: None

        """
        if kwargs is None:
            kwargs = {}
        user_code = self.catch_user_code(
            path=path,
            match=kwargs.get("match", None),
            code_count=kwargs.get("code_count", 1),
        )
        kwargs["user_code"] = user_code
        self.write(path, template_path, kwargs)

    def catch_user_code(self, path, match=None, code_count=1):
        """

        捕获目标路径文件中的用户代码

        :param path: 目标文件路径
        :param match: 匹配用户代码规则
        :param code_count: 用户代码数量
        :return: 匹配结果列表

        """
        if match is None:
            match = self.catch_match
        if not os.path.exists(path):
            return [""] * code_count
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        result = re.findall(match, content, re.S)
        result = list(map(lambda v: v.strip("\n "), result))
        size = len(result)
        if size < code_count:
            return result + [""] * (code_count - size)
        return result

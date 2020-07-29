from ..handlers.inheritHandler import AbstractBaseHandler
from ..rig import register
from ..rig.utils import require
from ..module import syncFile

import os
import shutil
import json

"""
freedom模块为了实现freedom file protocol，旨在使用一个API接口完成数据存储功能，
适用于高敏捷开发模式下不依赖后端逻辑，尽量在前端完成所有业务处理，通过接口直接提供
存储能力。

如需使用freedom file protocol请将模块的路由注释取消掉
"""

freedom = register.Router(prefix="/freedom/file/")


def create_json(path):
    """

    创建JSON文件，如果路径不存在会递归创建路径

    :param path: json文件创建路径
    :return: json文件创建路径

    """
    dir_path, file_name = os.path.split(path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(path, "w", encoding="utf-8") as fp:
        fp.write("{}")
    return path


def get_safe_path(self: AbstractBaseHandler, *path):
    """

    获取相对freedom的偏移路径，会判断请求路径是否安全，不会在
    之外的路径产生返回

    :param self: AbstractBaseHandler
    :param path: 路径
    :return: 正确的路径，否则触发400错误

    """
    fp = syncFile.Component("freedom")
    try:
        return fp.get_safe_path(*path)
    except AssertionError:
        return self.throw(400, "Illegal path")


@freedom.route(url=r"/(.+(?<!\.json)$)")
class FreedomPathHandler(AbstractBaseHandler):

    async def get(self, path):
        """

        获取路径下所有JSON文件列表

        调用地址::

            http://127.0.0.1:8095/freedom/*path

            get: *path代表具体路径与本地磁盘空间进行映射如foo路径下的bar http://127.0.0.1:8095/freedom/foo/bar

            可选参数：need_data(是否需要数据一起返回，*代表所有文件需要数据，如果只想取指定文件用逗号分隔)

        :param path: 查找路径
        :return: None

        """
        data_json_dir = get_safe_path(self, path)
        if not os.path.exists(data_json_dir):
            self.throw(404)

        need_data = self.get_argument("need_data", None)
        if need_data:
            if need_data == "*":
                paths = os.listdir(data_json_dir)
            else:
                paths = need_data.split(",")
            result = []
            for p in paths:
                json_path = get_safe_path(self, path, p)
                if os.path.exists(json_path):
                    result.append({"name": p, "data": require(json_path)})
            self.write_array(result)
        else:
            self.write_array(os.listdir(data_json_dir))

    async def post(self, path):
        """

        新增一个路径，递归添加

        调用地址::

            http://127.0.0.1:8095/freedom/*path

            post: *path代表具体路径与本地磁盘空间进行映射如foo路径下的bar http://127.0.0.1:8095/freedom/foo/bar

        :param path: 查找路径
        :return: None

        """
        data_json_dir = get_safe_path(self, path)
        if os.path.exists(data_json_dir):
            self.throw(200, "already exists")
        os.makedirs(data_json_dir)
        self.write_ok()

    async def put(self, path):
        """

        无内容

        :param path:
        :return:

        """
        self.throw(405)

    async def delete(self, path):
        """

        删除一个路径及其路径下的所有内容，危险操作

        调用地址::

            http://127.0.0.1:8095/freedom/*path

            delete: *path代表具体路径与本地磁盘空间进行映射如foo路径下的bar http://127.0.0.1:8095/freedom/foo/bar

        :param path: 查找路径
        :return: None

        """
        shutil.rmtree(get_safe_path(self, path))
        self.write_ok()


@freedom.route(url=r"/(.+\.json$)")
class FreedomHandler(AbstractBaseHandler):

    async def get(self, path):
        """

        返回指定路径下json文件内容，接受auto_create参数，是否当
        文件不存在时自动创建相应json文件并返回

        调用地址::

            http://127.0.0.1:8095/freedom/*path.json

            get: *path代表具体路径与本地磁盘空间进行映射如foo路径下的bar.json http://127.0.0.1:8095/freedom/foo/bar.json

            可选参数：auto_create(当文件不存在时，是否自动创建空文件并返回)

        :param path: 查找路径
        :return: None

        """
        data_json_path = get_safe_path(self, path)

        if not os.path.exists(data_json_path):
            auto_create = self.get_argument("auto_create", None)
            if auto_create:
                create_json(data_json_path)
                return self.write_dict({})
            else:
                self.throw(404)

        self.write_dict(require(data_json_path))

    async def post(self, path):
        """

        增加一个JSON文件，数据传入body并且以json格式传入

        调用地址::

            http://127.0.0.1:8095/freedom/*path.json

            post: *path代表具体路径与本地磁盘空间进行映射如foo路径下的bar.json http://127.0.0.1:8095/freedom/foo/bar.json

        :param path: 查找路径
        :return: None

        """
        data_json_path = get_safe_path(self, path)

        if os.path.exists(data_json_path):
            self.throw(200, "already exists")

        create_json(data_json_path)
        self.write_ok()

    async def put(self, path):
        """

        更新一个json文件

        调用地址::

            http://127.0.0.1:8095/freedom/*path.json

            put: *path代表具体路径与本地磁盘空间进行映射如foo路径下的bar.json http://127.0.0.1:8095/freedom/foo/bar.json

            body: 用JSON格式派发数据

        :param path: 查找路径
        :return: None

        """
        data_json_path = get_safe_path(self, path)

        if not os.path.exists(data_json_path):
            self.throw(404)

        with open(data_json_path, "w", encoding="utf-8") as fp:
            fp.write(json.dumps(self.get_body2json()))
        self.write_ok()

    async def delete(self, path):
        """

        删除一个json文件

        调用地址::

            http://127.0.0.1:8095/freedom/*path.json

            delete: *path代表具体路径与本地磁盘空间进行映射如foo路径下的bar.json http://127.0.0.1:8095/freedom/foo/bar.json

        :param path: 查找路径
        :return: None

        """
        data_json_path = get_safe_path(self, path)

        if os.path.exists(data_json_path):
            os.remove(data_json_path)

        self.write_ok()

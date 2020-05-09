from ..conf import parser

import os
import shutil
import uuid
import hashlib
from typing import Iterable, Tuple, Optional

option = parser.options("file")
print("[syncFile] is imported.\n")

"""
该模块和upload.py视图有关联，可以增加方法，但是不要修改或删除该组件内容
"""


class Component:
    """

    文件上下文处理模块

    :param path: 相对于root_path进行偏移的子文件，该类中通过get_safe_path来获取一个安全偏移的路径，防止输入超出文件路径的地址
    :param top_path: 默认情况从配置文件中获取，核心操作目录，有时需要把一些文件写入静态资源管理的文件夹中，可以修改它

    """

    def __init__(self, path="", top_path=None):
        if top_path:
            self.root_path = self.ajoin(top_path, path)
        else:
            self.root_path = self.ajoin(option["path"], path)

        self.write_chunk = self.read_chunk = 65536
        self.write_fp = self.read_fp = None
        self.encode = "utf-8"

    @staticmethod
    def ajoin(*args) -> str:
        """

        合并路径并转换成绝对路径

        :param args: 多个路径参数
        :return: 合并后且标准处理的路径

        """
        return os.path.abspath(os.path.join(*args))

    @staticmethod
    def join(*args) -> str:
        """

        合并的路径并经过标准化处理，去除..或.等符号

        :param args: 多个路径参数
        :return: 合并后且标准处理的路径

        """
        return os.path.normpath(os.path.join(*args))

    @staticmethod
    def ensure_dir(path: str) -> bool:
        """

        确保文件夹存在，不存在则创建它

        :param path: 文件夹路径
        :return: 返回判断之前是否存在该文件

        """
        if os.path.exists(path):
            return True
        else:
            os.makedirs(path)
            return False

    @staticmethod
    def touch(path: str) -> None:
        """

        快速创建一个空文件

        :param path: 文件路径
        :return: None

        """
        open(path, "wb").close()

    def get_safe_path(self, *args) -> str:
        """

        获取相对于self.root_path路径进行偏移子路径，如果合成后的子路径超出self.root_path路径
        会抛出AssertionError异常，有时希望通过用户传来的参数来构成一个路径，需要
        用到该方法，避免用户传递的参数中包含..等内容，最终导致路径位置偏移出限定目录中，接收多个路径合成参数

        :param args: 多个路径参数
        :return: 在限定路径下的子路径字符串

        """
        path = self.join(self.root_path, *args)
        assert self.root_path in path, "Path location overflow"
        return path

    def write(self, path: str, data: bytes, auto_close: bool = True) -> None:
        """

        向文件中写入数据，该方法编码为utf-8

        :param path: 文件路径
        :param data: 写入数据
        :param auto_close: 是否及时关闭文件流，如果设置False可以获取write_fp属性手动关闭
        :return: None

        """
        self.write_fp = open(path, "wb")
        self.write_fp.write(data)
        if auto_close:
            self.write_fp.close()
            self.write_fp = None

    def s_read(self, path: str, auto_close: bool = True) -> bytes:
        """

        不迭代数据，直接读取文件内容

        :param path: 读取文件的路径
        :param auto_close: 否及时关闭文件流，如果设置False可以获取read_fp属性手动关闭
        :return: bytes 读取到到的文件流

        """
        self.read_fp = open(path, "rb")
        data = self.read_fp.read()
        if auto_close:
            self.read_fp.close()
        return data

    def read(self, path: str, auto_close: bool = True) -> Iterable:
        """

        读取文件数据返回生成器

        :param path: 读取文件的路径
        :param auto_close: 是否及时关闭文件流，如果设置False可以获取read_fp属性手动关闭
        :return: generator

        """
        self.read_fp = open(path, "rb")
        while True:
            chunk = self.read_fp.read(self.read_chunk)
            if chunk:
                yield chunk
            else:
                break
        if auto_close:
            self.read_fp.close()
            self.read_fp = None
        return

    def is_exist(self, file_name: str) -> bool:
        """

        判断文件是否存在，需要[捕获异常]处理

        :param file_name: 文件名称
        :return: 布尔值，是否存在

        """
        file_path = self.get_safe_path(file_name)
        if os.path.exists(file_path):
            return True
        return False

    def is_exist_md5(self, md5: str, suffix: str) -> bool:
        """

        判断是否存在md5文件，用于分片上传的方法，需要[捕获异常]处理

        :param md5: md5值
        :param suffix: 文件后缀名称
        :return: 布尔值，是否存在

        """
        file_path = self.get_safe_path(md5 + "." + suffix)
        if os.path.exists(file_path):
            return True
        return False

    @staticmethod
    def clear_fragment(path: str) -> None:
        """

        清空指定文件夹，用于清理md5碎片文件夹

        :param path: 碎片路径
        :return: None

        """
        shutil.rmtree(path)

    def md5_to_file(self, fragment_path: str, md5: str, suffix: str) -> Iterable:
        """

        该功能为分片上传功能，用于合并分片上传产生的碎片块，需要[捕获异常]处理

        使用案例::

            file_context = syncFile.Component()
            for i in file_context.md5_to_file(fragment_path , md5, suffix):
                if not i:
                    return self.write_json(message="读取文件块产生错误，合并失败", status=1)
                # 提高并发，抛出当前handler控制主线程的权利
                await gen.sleep(0)
            self.write_json(message="合并成功")

        :param fragment_path: 碎片文件夹路径
        :param md5: md5值
        :param suffix: 文件后缀拓展名
        :return: None

        """
        md5_file = self.get_safe_path(md5 + "." + suffix)
        hmd5 = hashlib.md5()
        for i in range(len(os.listdir(fragment_path))):
            try:
                with open(os.path.join(fragment_path, str(i)), "rb") as fp:
                    block = fp.read()
                hmd5.update(block)
                with open(md5_file, "ab") as fp:
                    fp.write(block)
                yield True
            except IOError as e:
                yield False
        if hmd5.hexdigest() == md5:
            self.clear_fragment(fragment_path)
            return True
        return False

    def receive_file(self, files, arg_name="image", is_only=True, file_name=None) -> Optional[Tuple[str, str, str]]:
        """

        帮助tornado进行文件接收，该方法需要捕捉异常，只接收第一个文件
        接收路径会保证文件夹存在，不存在则创建，并且会查看是否为安全路径，不是
        安全路径抛出异常，需要[捕获异常]处理

        :param files: self.requests.files
        :param arg_name: 参数名称
        :param is_only: 是否生成唯一ID文件名
        :param file_name: 当is_only=False时，提供的自定义文件名称，如果不提供则来自上传的文件名，拓展名以上传文件为准无需附加
        :return: (文件名称[不携带拓展名]，文件保存本地地址，文件拓展名)

        """
        file_list = files.get(arg_name, None)
        if not file_list:
            return None

        # filename，body，content_type
        source_file = file_list[0]

        # 确保路径存在
        self.ensure_dir(self.root_path)
        source_name, source_ext = os.path.splitext(source_file.filename)
        source_ext = source_ext.lower()

        # 判断文件名称
        if is_only:
            name = str(uuid.uuid1())
        elif file_name:
            name = file_name
        else:
            name = source_name

        # 安全保存到本地
        save_path = self.get_safe_path(name + source_ext)
        self.write(save_path, source_file.body)

        return name, source_ext, save_path

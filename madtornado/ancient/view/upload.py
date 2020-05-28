from ..handlers.inheritHandler import Base
from ..rig import register
from ..module import syncFile
from ..rig import check

from tornado import gen

file_router = register.Router(prefix="/file")

"""
如果需要分块上传方案，请将三个类的路由注释取消掉，让路由可以正常注册
前端代码可以配合static/js下面的upload.js一起使用
"""


# @file_router.route(url="/exist")
class ExistFileHandler(Base):
    """

    获取md5文件是否存在

    文件分块上传接口::

        http://127.0.0.1:8095/file/exist

        get:访问

        需要参数：md5,suffix

        suffix标识后缀名，如png mp4 jpg等

    """

    async def get(self):
        md5 = self.get_argument("md5")
        suffix = self.get_argument("suffix")

        file_context = syncFile.Component("files")
        try:
            self.write_dict({"ieExist": file_context.is_exist_md5(md5, suffix)})
        except AssertionError as ae:
            self.throw(406, "非法请求")


# @file_router.route(url="/upload")
class UploadFileHandler(Base):
    """

    该模块为内置路由解决方案，提供文件分块上传参考
    如果需要可以取消掉路由注释，该路由模块将会自动注入到网站地图中

    文件分块上传接口::

        http://127.0.0.1:8095/file/upload

        post:访问

        需要参数：md5,file,block

    """

    async def post(self):
        """

        文件上传接口方法实现，参数处理比较复杂，新版本可以更加简洁，
        但是为了不破坏其它内容，并未修改逻辑

        """
        # 设置允许跨域
        # self.set_access_headers()

        arg = {
            "md5": self.get_argument("md5", None),
            "block": self.get_argument("block", None),
            "file": self.request.files.get("file", None)
        }

        message = check.some(arg, {
            "md5": check.not_null,
            "block": check.not_null,
            "file": check.not_null,
        })

        if message.status:
            file_context = syncFile.Component("fragment")
            try:

                md5_path = file_context.get_safe_path(arg["md5"])
                file_context.ensure_dir(md5_path)

                block_path = file_context.get_safe_path(md5_path, arg["block"])
                file_context.write(block_path, arg["file"][0].body)

                self.write_ok()

            except AssertionError as ae:
                self.throw(406, "非法请求")
        else:
            self.throw(406, "缺少{0}参数".format(message.key))


# @file_router.route(url="/merge")
class MergeFileHandler(Base):
    """

    文件分块上传合并文件接口::

        http://127.0.0.1:8095/file/merge

        post:访问

        需要参数：md5,suffix

        suffix标识后缀名，如png mp4 jpg等

    """

    async def post(self):
        # 设置允许跨域
        # self.set_access_headers()

        md5 = self.get_argument("md5", None)
        if not md5:
            self.throw(406, "缺少参数[md5]")

        suffix = self.get_argument("suffix", None)
        if not suffix:
            self.throw(406, "缺少参数[suffix]")

        fc = syncFile.Component("files")
        fc.ensure_dir(fc.root_path)

        frc = syncFile.Component("fragment")
        try:
            fragment_path = frc.get_safe_path(md5)
        except AssertionError:
            return self.throw(406, "非法请求")

        for b in fc.md5_to_file(fragment_path, md5, suffix):
            if not b:
                self.throw(400, "请求无法完成，未知错误")
            await gen.sleep(0)

        self.write_ok()

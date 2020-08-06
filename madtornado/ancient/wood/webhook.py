from ..handlers.inheritHandler import Base
from ..rig import register
from ..rig.utils import kill_form_port
from ..conf import c_parser

import os

"""
webhook模块允许你通过配置文件注册webhook以运行指定脚本程序。

如需使用freedom file protocol请将模块的路由注释取消掉
"""

webhook = register.Router(prefix="/webhook")
rf = register.rf
webhook_register_pool = c_parser.options("tornado-webhook")


# @webhook.route(url=rf.s("name").url)
class WebHook(Base):
    """

    允许你通过配置文件注册webhook以运行指定脚本程序

    访问地址::

        /webhook/:name(注册到配置文件的名称)

    配置举例::

        [tornado-webhook]
        example=c://example.bat|8095

        8095为部署程序的端口号，使用|分开脚本路径，如果指定则会根据该端口自动杀死程序进程，以进行重新自动部署，
        脚本为部署应用程序的详细执行过程，注意脚本路径只能是绝对路径

    """

    # async def get(self, name):
    #     await self.post(name)

    async def post(self, name):
        for i in webhook_register_pool:
            if name == i:
                cmd = c_parser["tornado-webhook"][i]
                result = cmd.split("|")
                if len(result) > 1:
                    kill_form_port(result[1])
                os.spawnv(os.P_NOWAIT, result[0], [result[0]])
                break
        self.write_ok()

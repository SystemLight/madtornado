from ..handlers.inheritHandler import Base
from ..rig import register
from ..rig.utils import kill_form_port, require, rinin
from ..conf import c_parser

from tornado.log import app_log

import os

"""

webhook模块允许你通过配置文件注册webhook以运行指定脚本程序。

如需使用webhook请将模块的路由注释取消掉

"""

webhook = register.Router(prefix="/webhook")
rf = register.rf

GOGS_CONF_PATH = c_parser.get("tornado-webhook", "gogs")


def exec_hook(name_conf):
    shell = name_conf.get("shell", None)
    app_port = name_conf.get("app_port", None)

    shell_path = os.path.abspath(shell)
    if app_port:
        kill_form_port(str(app_port))

    os.spawnv(os.P_NOWAIT, shell_path, [shell_path])
    app_log.info("Process: " + shell)


@webhook.route(prefix="gogs", url=rf.s("name").url)
class GogsWebHookHandler(Base):
    """

    允许你通过配置文件注册webhook以运行指定脚本程序，该指定脚本程序一般用于自动部署其它应用程序

    访问地址::

        /webhook/gogs/:name(注册到配置文件的名称)

    配置举例::

        [tornado-webhook]
        gogs=gogs webhook 配置文件路径

        {
          "注册name名称": {
            "shell": "C:\\netcoreapps\\update.bat", //执行脚本
            "analysis_execution": true, // 是否解析，当注册为windows服务时必须解析执行
            "app_port": 5000,  // 应用程序端口，用于自动部署该程序时自动重启该程序，可不填写，将不会重启应用
            "branch": [  // 当指定分支被推送时进行自动部署
              "master"
            ]
          }
        }

    """

    # async def get(self, name):
    #     await self.post(name)

    async def get(self, name):
        commit_data = self.get_body2json()
        now_branch = commit_data["ref"]

        conf = require(GOGS_CONF_PATH)
        name_conf = conf.get(name, None)

        if not name_conf:
            return self.throw(200, "No registered instructions")

        branch = name_conf.get("branch", None)
        if rinin(now_branch, branch) is None:
            return self.write_ok()

        exec_hook(name_conf)

        self.write_ok()

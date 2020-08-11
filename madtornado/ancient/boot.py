from .wood.webhook import exec_hook, GOGS_CONF_PATH, require

import os
import platform


def start_page(port):
    """

    自启动浏览器功能

    :param port: 访问地址的端口
    :return: None

    """
    if "Windows" == platform.system():
        os.system("start http://127.0.0.1:" + port)


def exec_hook_on_boot(names):
    """

    执行webhook脚本文件

    :param names: 部署任务名称，和注册文件中保持一致
    :return: None

    """
    for name in names:
        conf = require(GOGS_CONF_PATH)
        name_conf = conf.get(name, None)
        exec_hook(name_conf)


def boot():
    """

    这是入口程序，请在这里编写需要启动运行的程序内容

    :return: None

    """

    print("Boot hook is started")

    # 自启动浏览器，需要该功能请取消注释
    # start_page(c_parse.get("tornado", "port"))

    # 开机状态启动webhook脚本文件，用于自动更新唤醒部署
    # exec_hook_on_boot(["mad"])

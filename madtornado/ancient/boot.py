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


def boot():
    """

    这是入口程序，请在这里编写需要启动运行的程序内容

    :return: None

    """
    print("Boot hook is started")

    # 自启动浏览器，需要该功能请取消注释
    # start_page(c_parse.get("tornado", "port"))

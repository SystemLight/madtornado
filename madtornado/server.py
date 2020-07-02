#!/usr/bin/env python3
#
#   Copyright 2019 SystemLight
#   https://github.com/SystemLight/madtornado
#
# # # # # # # # # # #
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.options import define, options

import qrcode

import os
import json
from socket import gethostname, gethostbyname_ex

try:
    import ancient
except FileNotFoundError:
    boot_path = os.path.dirname(__file__)
    os.chdir(boot_path)
    print("Change Directory to [ " + boot_path + " ]")
    import ancient

ancient.boot()

opt = ancient.parser.options("tornado")
opt_server = ancient.parser.options("tornado-server")
opt_secret = ancient.parser.options("tornado-secret")
opt_static = ancient.parser.options("tornado-static")
opt_template = ancient.parser.options("tornado-template")
opt_proxy = ancient.parser.options("tornado-proxy")
opt_debug = ancient.parser.options("tornado-debug")


def default_routers():
    """

    捕获默认的静态路由，非装饰器注册的路由，这些路由一般是写死的且必要的
    当你需要多中不同前缀来访问静态资源目录时，不如试试去配置url_prefix=["/s"]

    :return: List

    """
    pong_route = (r"/pong", ancient.dealHandler.PongHandler)

    static_routes = []
    default_filename = opt_static["default_filename"]
    default_static_path = opt_static["default_static_path"]
    for p in json.loads(opt_static["url_prefix"]):
        path = None
        df = None
        if type(p) == str:
            prefix = p
        else:
            prefix = p[0]
            if len(p) > 1:
                path = p[1]
            if len(p) > 2:
                df = p[2]
        static_routes.append((prefix + "/(.*)", ancient.dealHandler.StaticHandler, {
            "path": path or default_static_path,
            "default_filename": df or default_filename,
            "prefix": prefix,
        }))
    static_route = (r"/(.*)", ancient.dealHandler.StaticHandler, {
        "path": default_static_path,
        "default_filename": default_filename,
    })

    proxy_prefix = opt_proxy["proxy_prefix"]
    proxy_handler = json.loads(opt_proxy["proxy_handler"])
    proxy_routes = []
    for alias, address in proxy_handler:
        partner = filter(lambda x: x, [proxy_prefix, alias, r".*"])
        address = address.rstrip("/")
        url = "/" + "/".join(partner)
        host = address.split("://")[1]
        proxy_routes.append(
            (url, ancient.dealHandler.ProxyHandler, {
                "proxy_option": {"instead": url.rstrip("/.*"), "address": address, "host": host}
            }))

    return [pong_route, *proxy_routes, *static_routes, *ancient.end_register_route, static_route]


def routers():
    """

    生成tornado的路由，将静态路由，和动态注册的路由合并

    :return: List

    """
    ancient.register_route.extend(default_routers())
    with open("log/webMap.log", "w", encoding="utf-8") as web_map:
        for r in ancient.register_route:
            web_map.write(str(r[0]) + "\n")
    print("The site map is generated !")
    return ancient.register_route


def set_log():
    """

    配置tornado的日志函数，DEBUG < INFO < WARNING < ERROR < CRITICAL

    :return: None

    """
    options.logging = "DEBUG"
    options.log_file_prefix = "log/torStatus{0}.log".format(options.port)
    options.log_rotate_mode = "time"
    options.log_rotate_when = "D"
    options.log_rotate_interval = 1
    print("Enable log files : {}".format("log/torStatus{0}.log".format(options.port)))


def print_qrcode(url):
    """

    根据传入url生成二维码打印到控制台，便于移动端调试页面

    :param url: 网站主页地址
    :return: None

    """
    qr = qrcode.QRCode(version=1, border=1)
    qr.add_data(url)
    qr.print_ascii(invert=True)


def print_info():
    """

    打印服务器信息

    :return: None

    """
    print("Whether to publish: {}".format(opt["release"]))
    print("****************************************************")
    frame = opt["frame"]
    project = opt["project"]
    print("The frame name is {}".format(frame))
    print("The current version of {} is {}".format(frame, opt["frame_version"]))
    print("****************************************************")
    print("The project name is {}".format(project))
    print("The current version of {} is {}".format(project, opt["project_version"]))
    print("****************************************************")


def application():
    """

    生成一个可用的应用程序，供http服务器调用

    :return: Application

    """
    settings = {
        "autoescape": "xhtml_escape",
        "websocket_ping_interval": None,

        # "static_path": "statics",
        # "static_url_prefix": "/static",
        "template_path": opt_template["template_path"],
        "cookie_secret": opt_secret["cookie_secret"],
        "xsrf_cookies": opt_secret["xsrf_cookies"] == "true",

        "ui_methods": ancient.uiMethod,
        "ui_modules": ancient.uiModule.registered_class,

        "debug": opt_debug["debug"] == "true",
        "autoreload": opt_debug["autoreload"] == "true",
        "compiled_template_cache": opt_debug["compiled_template_cache"] == "true",
        "static_hash_cache": opt_debug["static_hash_cache"] == "true",
        "serve_traceback": opt_debug["serve_traceback"] == "true",
    }
    domain_name = opt_server["domain"]
    if domain_name:
        app = Application(handlers=None, **settings)
        app.add_handlers(domain_name, routers())
        print("Local access : [ http://127.0.0.1:{} ]".format(options.port))
        print("Remote access : [ http://{0}:{1} ]".format(domain_name, options.port))
    else:
        app = Application(handlers=routers(), **settings)
        print("Local access : [ http://127.0.0.1:{} ]".format(options.port))
        network_index = int(opt_debug["network_index"])
        index = 0
        for ip in gethostbyname_ex(gethostname())[2]:
            index += 1
            url = "http://{}:{}".format(ip, options.port)
            print("Remote access : [ {} ]".format(url))
            if network_index == index:
                print_qrcode(url)
    return app


def main():
    """

    主函数入口，用于将应用注册到httpserver，并开启事件循环

    :return: None

    """
    define("port", default=int(opt_server["port"]), type=int, help="Run on the given port")
    print_info()
    if opt_debug["open_log"] == "true":
        set_log()
    options.parse_command_line()
    http_server = HTTPServer(application(), xheaders=opt_proxy["xheaders"],
                             max_buffer_size=128 * 1024 * 1024, max_body_size=128 * 1024 * 1024)
    http_server.bind(options.port, opt_server["listen"])
    http_server.start(1)
    print("Site initialization is successful !")
    IOLoop.current().start()


if __name__ == "__main__":
    main()

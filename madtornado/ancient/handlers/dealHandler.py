from .inheritHandler import Base

from tornado.httpclient import AsyncHTTPClient, HTTPClientError
from tornado.web import StaticFileHandler

"""
改模块下包含一些基类，可以通过配置文件控制这些基类的反应行为
"""


class StaticHandler(StaticFileHandler, Base):
    """

    继承 `StaticFileHandler` 和 `BaseHandler` ，用于处理静态文件访问控制的类，

    """

    def initialize(self, path: str, default_filename: str = None, prefix: str = None) -> None:
        super(StaticHandler, self).initialize(path, default_filename)
        self.prefix = prefix
        self.absolute_path = path  # 缺少这个属性web.py会报错，问题不大

    # @override
    async def get(self, path, include_body=True):
        """

        默认等于StaticFileHandler.get()行为，通过写该方法，对文件进行控制，可以直接在这里编写代码

        结合单页面应用使用，请改写成以下内容，可以替换index.html为自己的单页面::

            if not self.prefix:
                try:
                    await super(StaticHandler, self).get(path, include_body)
                    return
                except Exception as e:
                    await super(StaticHandler, self).get("index.html", include_body)
                    return
            else:
                await super(StaticHandler, self).get(path, include_body)

        """
        await super(StaticHandler, self).get(path, include_body)


class ProxyHandler(Base):
    """

    默认情况代理模块一定带有proxy前缀，可以在配置文件中更改proxy_prefix属性内容

    代理服务采用流式请求远端服务器和流式返回内容的方式，即Transfer-Encoding: chunked

    注意：代理请求根路径访问时结尾一定要加"/",如http://你的域名/proxy/bd/，否则不进行代理

    在配置文件中，填写proxy_handler用来启用代理模块::

        proxy_handler = [["p1","http://www.baidu.com"],["p2","http://www.google.com/"]]

    上述配置了两个代理路由，访问URL如下：

    1. 第一个:http://你的域名/proxy/p1/要访问的地址，这将代理到baidu下面

    2. 第二个:http://你的域名/proxy/p2/要访问的地址，这将代理到google下面

    proxy_prefix和alias(也就是配置中的p1或p2)可以为空，但是不能包含"/"

    代理路径是 http://你的域名/proxy_prefix/alias/要访问的路径

    .. attribute:: proxy_address

        代理地址关键信息，包含{instead, address, host}

    """

    def __init__(self, application, request, **kwargs):
        super(ProxyHandler, self).__init__(application, request, **kwargs)

        self.is_status = True
        self.proxy_code = 200
        self.__proxy_option = self.__proxy_option or None

    # @override
    def initialize(self, **kwargs):
        """

        __init__之前回调的方法

        :param kwargs: __proxy_address
        :return: None

        """
        self.__proxy_option = kwargs.get("proxy_option", None)

    # @override
    async def prepare(self):
        """

        预处理回调，在请求开始之前执行的内容，设置允许跨域

        :return: None

        """
        await super(ProxyHandler, self).prepare()
        self.set_access_headers()

    # @override
    async def options(self):
        """

        符合下列条件，会跨域预检::

            1. 请求方法不是GET/HEAD/POST
            2. POST请求的Content-Type并非application/x-www-form-urlencoded, multipart/form-data, 或text/plain
            3. 请求设置了自定义的header字段

        :return: None

        """
        self.set_access_headers()

    # @override
    async def get(self):
        """

        GET方法请求代理

        :return: None

        """
        await self.proxy()

    # @override
    async def post(self):
        """

        POST方法请求代理

        :return:  None

        """
        await self.proxy()

    # @override
    async def put(self):
        """

        PUT方法请求代理

        :return: None

        """
        await self.proxy()

    # @override
    async def delete(self):
        """

        DELETE方法请求代理

        :return:  None

        """
        await self.proxy()

    def proxy_received_header(self, chunk):
        """

        处理收到的头部信息

        :param chunk: 收到的一行头部信息
        :return: None

        """
        if self.is_status:
            self.is_status = False
            self.proxy_code = int(chunk.split(" ")[1])
        elif chunk == "\r\n":
            self.set_status(self.proxy_code)
            self.set_header("Proxy", "madtornado")
        else:
            if not next((code for code in [
                "Transfer-Encoding",
                "Content-Length",
                "Server",
            ] if code in chunk), None):
                if "Content-Type" in chunk:
                    self.set_header("Content-Type", chunk.split(":")[1].strip(" \r\n"))
                else:
                    self._headers.parse_line(chunk)

    def proxy_received_body(self, chunk):
        """

        处理收到的body信息

        :param chunk: 收到的body块
        :return: None

        """
        self.write(chunk)
        self.flush()

    async def proxy(self):
        """

        访问代理::

            http://域名/proxy/自定义后缀/代理的内容路径

        :return:  None

        """
        if not self.__proxy_option:
            self.throw(404)
            return

        opt = self.__proxy_option

        req_uri = opt["address"] + self.request.uri.replace(opt["instead"], "")
        body = self.request.body if self.request.body else None
        method = self.request.method
        headers = self.request.headers
        headers["Host"] = opt["host"]
        try:
            await AsyncHTTPClient().fetch(req_uri, method=method, body=body, headers=headers,
                                          validate_cert=False, request_timeout=10,
                                          header_callback=self.proxy_received_header,
                                          streaming_callback=self.proxy_received_body)
        except HTTPClientError as e:
            if e.code > 555:
                self.throw(e.code)


class PongHandler(Base):
    """

    有时可能需要测试服务器的服务是否启动，请访问/init，来进行确定

    """

    # @override
    async def get(self):
        """

        有时可能需要测试服务器的服务是否启动，请访问/init，来进行确定

        """
        self.throw(200, log_message="connected")

    # @override
    async def post(self):
        """

        有时可能需要测试服务器的服务是否启动，请访问/init，来进行确定

        """
        await self.get()

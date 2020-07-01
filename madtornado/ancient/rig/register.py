register_route = []
end_register_route = []


class Router:
    """

    如果不需要分组可以直接在Handler上面增加装饰器，如::

        @register.route(version="v3")
        class RecpHandler(BaseHandler):
            ...

        访问地址：http://127.0.0.1:8095/v3/recp

    分组路由，如::

        实例化router对象
        router=register.Router(prefix="/prefix",version="v3")

        @router.route()
        class RecpHandler(BaseHandler):
            ...

        @router.route(url="/custom")
        class NewRecpHandler(BaseHandler):
            ...

        访问地址：http://127.0.0.1:8095/v3/prefix/recp
        访问地址：http://127.0.0.1:8095/v3/perfix/custom

    :param version: restful风格版本号
    :param prefix: 统一路由前缀

    """

    def __init__(self, version="", prefix=""):
        self.version = version.strip("/\\")
        self.prefix = prefix.strip("/\\")

    @staticmethod
    def get_pe8(content: str):
        """

        将大写字母分割转换成下划线分割的形式，如AbcDef-->abc_def

        :param content: 转换的类名，如果带有Handler结尾将自动去除
        :return: 转换后的内容

        """
        if content.endswith("Handler"):
            content = content[:-7]
        for i in filter(lambda x: x.isupper(), content):
            content = content.replace(i, "_" + i.lower())
        return content.strip("_")

    def route(self, prefix: str = "", url: str = None, urls: list = None, end=False):
        """

        ``装饰器`` 添加该装饰器的请求实例，路由路径会被自动注册到路由表中
        如果你并不想使用装饰器，你可以直接获取register.register_route的
        路由表进行添加内容，通过装饰器注册的类是不区分顺序的，完全类导入顺序
        路由具体生成顺序可以在运行程序后查看log下面的webMap.log文件

        是否需要路由结尾有/和没有/匹配的地址一样，例如index/和index匹配是一样的
        你可以设置url参数如/index/abc/?，这样两个匹配效果是一样的

        如果你在配置文件中配置了url_prefix = [] 这是一个列表，会生成一组带前缀的静态文件路由匹配项
        而我们的end=True的路由会放到这些带前缀的静态文件管理路由后面

        :param prefix: 如果提供该内容将在路由中添加一个前缀，这个前缀是在统一路由前缀后面的
        :param url: 路由路径，不填写默认会根据类名生成路径
        :param urls: 如果设置该参数，传入一个列表对象，url将不起效果，同时为该类增加多个可匹配的路由
        :param end: 声明该路由是否注册到默认路由后面，系统默认路由参考server.py中的default_route
        :return: None

        """
        global register_route
        prefix = prefix.strip("/\\")

        def add_route(func):
            if urls:
                routes = map(lambda x: x.lstrip("/\\"), urls)
            elif url:
                routes = [url.lstrip("/\\")]
            else:
                routes = [self.get_pe8(func.__name__)]
            path = "/".join(filter(lambda x: x, [self.version, self.prefix, prefix]))
            path = "/" + path if path else ""
            for r in routes:
                if end:
                    end_register_route.append(("{}/{}".format(path, r), func))
                else:
                    register_route.append(("{}/{}".format(path, r), func))

            return func

        return add_route


route = Router().route

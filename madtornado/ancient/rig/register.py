register_route = []
end_register_route = []


def _url(match, union):
    """

    当union为true时，替换掉字符中+和*符号

    :param match: 匹配字符串
    :param union:
    :return: 清洗后的字符串

    """
    return match.replace("*", "").replace("+", "") if union else match


class RESTful:
    """

    RESTful风格路由生成器，用于快速生成restful风格路由，
    生成的路由可以被注册，不建议过长的路由匹配，尽量使用querystring
    进行参数传递

    示例一::

        rf = register.rf

        # 以对象的方式描写RESTful风格路由，相当于
        # /zoos/{动物园ID}/animals               # 动物园所有动物
        # /zoos/{动物园ID}/animals/{动物ID}       # 动物园指定ID的动物
        @register.route(url=rf.e("zoos").e("animals").url)

    示例二::

        # 与上述注册方式效果一致
        @register.route(url=RESTful(["zoos", "animals"]).u())
        @register.route(url=RESTful([("zoos","(正则的类型，斜杠)w"), "animals"]).url)

    示例三::

        # 压缩实体去掉前缀路径，使用s方法注册的实体不包含前缀，即/{动物园ID}
        @register.route(url=rf.s("zoos").url)

        # 控制实例ID标识项是否可以省略，默认是可省略的标识
        @register.route(url=rf.e("zoos").u(rf.LOOSE))

        # 严格模式下必须包含指定的动物园ID，即无法匹配 /zoos
        @register.route(url=rf.e("zoos").u(rf.STRICT))

    示例四::

        有时你可能需要匹配的参数是可选的，你可以这样注册
        url=rf.e("fruit", **rf.union("apple", "banana", "orange")).url

        上面的注册只会对三条路径进行匹配，使用union方法创造可选匹配串，通过**的方式传递给实体方法
        /fruit/apple，/fruit/banana，/fruit/orange

    """
    LOOSE = 0
    STRICT = 1
    IGNORE = 2

    def __init__(self, init_entity=None):
        self.entity = []
        self.eof = r"(?:/({}*))?"
        self.chain = r"/({}+)"

        if init_entity:
            for ie in init_entity:
                if isinstance(ie, str):
                    self.e(ie)
                elif isinstance(ie, tuple):
                    self.e(*ie)

    @staticmethod
    def union(*args):
        """

        返回一个用于shape参数的匹配字符串，代表该内容类型为可选内容，可选范围为传入的内容

        :param args: 可选项的列表
        :return: 用于shape参数的匹配字符串

        """
        return {"shape": "|".join(args), "union": True}

    def e(self, name, shape=r"[^\\/]", union=False):
        """

        URL中增加一个实体，实体是有前缀的，前缀名等于name

        :param name: 实体前缀名称
        :param shape: 匹配类型
        :param union: 类型是否为可选匹配
        :return: RESTful实例对象

        """
        self.entity.append({
            "name": "/" + name,
            "shape": shape,
            "union": union,
        })
        return self

    def s(self, name, shape=r"[^\\/]", union=False):
        """

        URL中增加一个简易实体，实体没有前缀

        :param name: 实体前缀名称，仅用于标记无实际意义
        :param shape: 匹配类型
        :param union: 类型是否为可选匹配
        :return: RESTful实例对象

        """
        self.entity.append({
            "name": "",
            "shape": shape,
            "union": union,
        })
        return self

    def clear(self):
        """

        清空注册进来的内容

        :return: RESTful实例对象

        """
        self.entity = []
        return self

    @property
    def url(self):
        """

        属性方法，获取url

        :return: 生成的URL匹配串

        """
        return self.u(int(len(self.entity) == 1 and not self.entity[0]["name"]))

    def u(self, need_eof=0):
        """

        获取url

        :param need_eof: 结尾字符的种类
        :return: 生成的URL匹配串

        """
        result = ""
        size = len(self.entity) - 1
        for idx, e in enumerate(self.entity):
            result += e["name"]
            if idx == size:
                if need_eof == 0:
                    result += _url(self.eof, e["union"]).format(e["shape"])
                elif need_eof == 1:
                    result += _url(self.chain, e["union"]).format(e["shape"])
                else:
                    break
            else:
                result += _url(self.chain, e["union"]).format(e["shape"])
        result += r"$"
        self.clear()
        return result


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
rf = RESTful()

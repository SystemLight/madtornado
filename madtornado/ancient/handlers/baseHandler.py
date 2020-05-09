from ..model.response import ResponseModel

from tornado import escape
from tornado.web import RequestHandler, HTTPError

import time
from json.decoder import JSONDecodeError


class BaseHandler(RequestHandler):
    """

    通过继承 `BaseHandler` 来使用它提供的便利方法，任何一条访问都是一个继承了 `BaseHandler` 的实例化对象
    在0.3之后的版本，不建议直接继承BaseHandler，而是通过inheritHandler下的Base间接继承，这样你可以很轻松
    的更改路由的父类，如你突然想要给这些子类加入拦截验证功能，你只需要改变inheritHandler/Base的指向就够了。

    :param application: tornado.web.Application对象
    :param request: HTTPServerRequest对象 (protocol,host,method,uri,version,remote_ip)
    :param kwargs: 其它在application加入到路由表时添加的额外字段

    .. attribute:: request

        The `tornado.httputil.HTTPServerRequest` object containing additional
        request parameters including e.g. headers and body data::

            request(uri,host,method,header,body,path,query,version,remote_ip,files)

    .. attribute:: talks_name

        token或者session id 返回的cookie名称

    .. attribute:: json_body

        当使用get_json_body方法后用于保存转换成json的body内容

    HTTPFile(request.files)::

        self.request.files.get()方法，获取名称对应的file列表
        file文件拥有属性，filename，body，content_type

    """

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

        self.talks_name = "MtKey"
        self.json_body = None

        self.cross_domain = None

    # @override
    def initialize(self):
        """

        ``重写方法`` 当实例还没有生成之前会调用的函数

        :return: None

        """
        pass

    # @override
    def data_received(self, chunk):
        """

        ``重写方法`` 类加上 `@stream_request_body` 装饰器以后，自动调用的方法

        :param chunk: 传入body中的流文件
        :return: None

        """
        pass

    # @override
    def get_login_url(self):
        """

        ``重写方法`` 自定义login_url地址，返回url地址，当使用@authenticated装饰器时，未验证的连接将跳转的url

        :return: str

        """
        pass

    # @override
    async def prepare(self):
        """

        ``重写方法`` 当实例连接进来需要预先处理内容时调用的函数，例如token认证等任务，写在其中,
        不建议直接修改BaseHandler的该方法，应当继承BaseHandler后，重写该方法，并且之后拥有相同
        行为的Handler，继续继承同一个被改写prepare的Handler的类

        :return: None

        """
        pass

    # @override
    def on_finish(self):
        """

        ``重写方法`` 当连接完成所有工作后，收尾时调用的方法，可以写入如sql关闭等任务，与prepare方法一样，
        不建议直接改写BaseHandler的该方法，会影响到所有继承BaseHandler的类

        :return: None

        """
        pass

    # @override
    def on_connection_close(self):
        """

        ``重写方法`` 当连接被意外断开时调用的方法，这个为tornado自带方法，内部有一定处理程序，不建议直接继承重写该方法，
        正确的做法是继承BaseHandler对象，重写它的on_close方法

        :return: None

        """
        super(BaseHandler, self).on_connection_close()
        self.on_close()

    def on_close(self):
        """

        当连接被意外断开时调用的方法，继承BaseHandler的类可以直接重写该方法

        :return: None

        """
        pass

    # @override
    def write_error(self, status_code, **kwargs):
        """

        ``重写方法`` 当send_error方法被触发时，调用的方法，用来处理错误状态
        想要触发原始错误信息，请使用send_error

        想要使用json格式错误信息，请使用throw方法

        使用send_error会触发tornado系统默认处理，请使用throw触发madtornado来处理错误

        :param status_code: 状态码
        :param kwargs: 额外参数，如exc_info包含HTTPError的错误信息元组
        :return: None

        """
        if self.cross_domain:
            self.set_access_headers(self.cross_domain)
        if "exc_info" in kwargs:
            exception = kwargs["exc_info"][1]
            log_message = exception.log_message if hasattr(exception, "log_message") else ""
            self.write_resp(status_code, log_message=log_message, **kwargs)
            self.finish()
        else:
            super(BaseHandler, self).write_error(status_code, **kwargs)

    def write_resp(self, status_code, **kwargs):
        """

        restful风格的自定义错误数据，该错误返回JSON格式错误响应
        重写该方法用于自定义错误响应格式，该方法重新时不要抛出错误异常或调用send_error，throw等

        :param status_code: 响应码
        :param kwargs: 额外参数和log_message
        :return: None

        """
        resp = ResponseModel()
        self.set_header('Content-Type', "application/json; charset=UTF-8")
        resp.status_code = status_code
        resp.reason = self._reason
        resp.message = kwargs.get("log_message", "")
        self.write(resp.get())

    def throw(self, status_code=200, log_message="", **kwargs):
        """

        send_error()方法并不会直接触发系统默认的错误处理样式，如果想使用默认错误处理返回的内容，
        请使用throw()方法，注意该方法会被try捕获到，如果写入到try中的时候请注意

        常用状态码::

            400 - 请求出现错误，非常通用，不想明确区分的客户端请求出错都可以返回
            401 - 没有提供认证信息，未登录或者用户名密码错误
            403 - 请求的资源不允许访问，token过期
            404 - 请求的内容不存在
            405 - 请求的[ 方法 ]不允许使用
            406 - 请求格式不正确
            408 - 请求超时了
            410 - 请求资源曾经存在，但现在不存在了
            413 - 请求体过大
            414 - 请求的 URI 太长了
            415 - 不支持的媒体类型

        :param status_code: 状态码
        :param log_message: 返回消息
        :param kwargs: 额外参数，如{'status_code': 404, 'reason': None}
        :return: None

        """
        raise HTTPError(status_code, log_message=log_message, **kwargs)

    def write_ok(self):
        """

        返回一个正常的状态，这个方法和self.throw(200)返回内容是一样的，
        但是throw方法会被捕获异常所捕获到，write_ok并不会被捕获

        :return: None

        """
        self.write_resp(200)

    def write_dict(self, dict_data, encode_date=False):
        """

        返回JSON数据响应，该返回为纯粹的数据，错误信息根据状态码进行判定,

        :param dict_data: dict类型数据
        :param encode_date: 是否存在datetime类型的字段
        :return: None

        """
        self.write_array(dict_data, encode_date)

    def write_array(self, list_data, encode_date=False):
        """

        返回JSON数据响应，对象数组

        :param list_data: 列表数据
        :param encode_date: 是否存在datetime类型的字段
        :return: None

        """
        self.set_header('Content-Type', "application/json; charset=UTF-8")
        self.write(ResponseModel.dumps(list_data, encode_date))

    def write_jsonp(self, key, value):
        """

        当使用jsonp技术进行请求时，调用此方法，用来直接返回jsonp的内容

        :param key: jsonp的名称
        :param value: 返回jsonp的内容，多个内容用逗号分隔
        :return: None

        """
        self.set_header("Content-Type", "application/x-javascript; charset=UTF-8")
        jc = self.get_argument(key, None)
        self.write(str(jc) + '(' + value + ')')

    def get_body2json(self):
        """

        获取请求的body，将其转换成json数据，并保存在属性json_body中

        :return: dict

        """
        if type(self.json_body) is not dict:
            try:
                self.json_body = escape.json_decode(self.request.body)
            except JSONDecodeError as e:
                self.json_body = {}
        return self.json_body

    def get_body_argument_for(self, these=None):
        """

        获取一组body中的form-url格式参数

        :param these: 一个字典对象，包含要获取的参数名称和对应的默认值，如果为None获取所有值
        :return: dict 获取完成的字典对象，参数名和值相对应

        """
        return self.__get_arg(these, self.request.body_arguments, self.get_body_argument)

    def get_query_argument_for(self, these=None):
        """

        获取一组query中的form-url格式参数

        :param these: 一个字典对象，包含要获取的参数名称和对应的默认值，如果为None获取所有值
        :return: dict 获取完成的字典对象，参数名和值相对应

        """
        return self.__get_arg(these, self.request.query_arguments, self.get_query_argument)

    def get_argument_for(self, these=None):
        """

        获取一组query中或者body中的form-url格式参数

        :param these: 一个字典对象，包含要获取的参数名称和对应的默认值，如果为None获取所有值
        :return: dict  获取完成的字典对象，参数名和值相对应

        """
        return self.__get_arg(these, self.request.arguments, self.get_argument)

    @staticmethod
    def __get_arg(these, arguments, get_argument):
        """

        私有方法，用于批量获取参数

        :param these: 一个字典对象，包含要获取的参数名称和对应的默认值，如果为None获取所有值
        :param arguments: 可以取到所有参数的容器
        :param get_argument: 获取参数的方法函数
        :return: dict  获取完成的字典对象，参数名和值相对应

        """
        content = {}
        if these is None:
            for arg in arguments:
                content[arg] = arguments[arg][-1].decode("utf-8")
        else:
            for arg in these:
                content[arg] = get_argument(arg, these[arg])
        return content

    def get_body_argument_from(self, these_list):
        """

        根据传入的参数列表获取参数，如果参数为空值则不返回，从body中查找参数

        :param these_list: 想要获取的参数的列表
        :return: dict 根据these_list提供的参数列表所能取到的变量键值对

        """
        return self.__get_arg_from(these_list, self.get_body_argument)

    def get_query_argument_from(self, these_list):
        """

        根据传入的参数列表获取参数，如果参数为空值则不返回，从query中查找参数

        :param these_list: 想要获取的参数的列表
        :return: dict 根据these_list提供的参数列表所能取到的变量键值对

        """
        return self.__get_arg_from(these_list, self.get_query_argument)

    def get_argument_from(self, these_list):
        """

        根据传入的参数列表获取参数，如果参数为空值则不返回，从body和query中查找参数

        :param these_list: 想要获取的参数的列表
        :return: dict 根据these_list提供的参数列表所能取到的变量键值对

        """
        return self.__get_arg_from(these_list, self.get_argument)

    @staticmethod
    def __get_arg_from(these_list, get_argument):
        """

        私有方法，根据传入的参数列表获取参数，如果参数为空值则不返回

        :param these_list: 想要获取的参数的列表
        :return: dict 根据these_list提供的参数列表所能取到的变量键值对

        """
        content = {}
        for key in these_list:
            result = get_argument(key, None)
            if result:
                content[key] = result
        return content

    def get_argument_plus(self, arg_name, arg_default=None):
        """

        获取任意格式传入的参数，可以参数写在链接中，也可以写在body中用json形式保存，也可以x-www-form-urlencoded形式传入body，
        调用该方法将自动识别，不支持formdata类型获取，请使用request.files属性自行获取，或者通过data_received回调方法获取

        :param arg_name: 参数名称
        :param arg_default: 获取不到返回的默认值
        :return: 经过处理获取到的值

        """
        content = self.get_argument(arg_name, None)
        if content is not None:
            return content
        content = self.get_body2json().get(arg_name, None)
        if content is not None:
            return content
        return arg_default

    def get_current_user(self):
        """

        当使用 `tornado.web.authenticated` 装饰器时调用的方法，如果返回内容，则验证通过，否则自动调整到登录页面，登录地址
        设置application中的'login_url': '',参数

        :return: str 当前用户的cookie信息

        """
        return self.get_secure_cookie(self.talks_name)

    def set_current_user(self, value, over_time=3600):
        """

        设置用户会话cookie

        :param value: 值，可以是token，也可以是session id
        :param over_time: 过期时间
        :return: None

        """
        self.set_secure_cookie(self.talks_name, value, expires=self.expires_time(over_time))

    def clear_current_user(self):
        """

        清除用户会话cookie

        :return: None

        """
        self.clear_cookie(self.talks_name)

    def set_default_headers(self):
        """

        ``重写方法`` 当返回响应的时候，需要设置header信息，调用的默认方法，BaseHandler默认采用text/html方式返回

        :return: None

        """
        self.set_header("Content-Type", "text/html; charset=UTF-8")

    def set_stream_headers(self, name):
        """

        设置返回为流类型，一般用于文件下载

        :param name: 文件名称
        :return: None

        """
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + name.encode('utf-8').decode('ISO-8859-1'))

    def set_nocache_headers(self):
        """

        设置不缓存该文件

        :return: None

        """
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

    def set_access_headers(self, domain='*'):
        """

        设置允许跨域访问

        :param domain: 域范围
        :return: None

        """
        self.set_header('Access-Control-Allow-Origin', domain)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Methods', 'PUT,POST,GET,DELETE,OPTIONS')
        self.set_header('Access-Control-Max-Age', 600)
        self.cross_domain = domain

    @staticmethod
    def expires_time(e_time):
        """

        对cookie过期时间进行过滤

        :param e_time: 过期时间，如3600秒
        :return: 赋值给expires的真实值

        """
        return time.time() + e_time

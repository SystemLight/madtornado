from ..handlers.baseHandler import BaseHandler

"""

为什么会有该模块能，该模块为了方便更改view中模块继承的基类
试想一下如果你某个模块改变了，你要让每个view中模块都改继承该类
你就需要一个一个的更改它们的继承父类，这很恶心，所以所有的子类
都继承该模块中的类，这些类只是一个别称，让你可以更加灵活的替换
父类

"""


class CustomErrorBaseHandler(BaseHandler):
    """

    madtornado全面使用restful风格规范，并且错误处理分割已经预定义为JSON格式响应，如果想自定义
    JSON的数据内容可以调用时传参self.throw(404，log_message="message content")

    如果想自定义一类错误处理，可以如该模块一样重写write_resp，并且做拦截，注意你也许并不是所有请求方法
    下都需要拦截并自定义处理错误，请对请求方法和错误码进行判断，之后你可以让拥有相同错误处理方式的类都继承该类

    """

    def write_resp(self, status_code, **kwargs):
        """

        重写write_resp错误响应方法，该方法中切记不要调用任何抛出异常或者send_error，throw方法
        否则会一直递归调用，请在结尾处调用父类该方法，保证其它响应异常可以被正确处理

        该类是一个自定义响应信息处理类，当GET方法并且响应404时返回自定义的内容，其余交给父类处理用resultful风格
        当你使用send_error方法抛出响应状态时，该方法不执行，因为send_error是tornado的方法，错误处理由tornado直接
        进行，请使用madtornado的方法throw()抛出响应异常

        :param status_code: 响应状态码
        :param kwargs: 额外参数和log_message
        :return: None

        """
        if self.request.method == "GET" and status_code == 404:
            return self.write('<h1 style="text-align:center">404 : madtornado can\'t find</h1>')
        super(CustomErrorBaseHandler, self).write_resp(status_code, **kwargs)


class InterceptorBaseHandler(BaseHandler):
    """

    该类可以作为一个验证拦截器，你可以继承该类之后你需要重写interceptor
    在该方法中做权限验证，这个拦截器目前只作用于get，post，put，delete方法
    并且你要书写的请求也不是在get等中了，而是派生的i_get，i_post，i_put，i_delete

    举例::

        async def i_get(self):
            ...

        async def i_post(self):
            ...

    """

    async def interceptor(self, *args):
        """

        重写该方法

        :return: 返回True则继续执行，返回False将不继续执行

        """
        ...

    async def get(self, *args):
        inter = await self.interceptor(*args)
        if not inter:
            return
        await self.i_get(*args)

    async def i_get(self, *args):
        ...

    async def post(self, *args):
        inter = await self.interceptor(*args)
        if not inter:
            return
        await self.i_post(*args)

    async def i_post(self, *args):
        ...

    async def put(self, *args):
        inter = await self.interceptor(*args)
        if not inter:
            return
        await self.i_put(*args)

    async def i_put(self, *args):
        ...

    async def delete(self, *args):
        inter = await self.interceptor(*args)
        if not inter:
            return
        await self.i_delete(*args)

    async def i_delete(self, *args):
        ...


Base = BaseHandler

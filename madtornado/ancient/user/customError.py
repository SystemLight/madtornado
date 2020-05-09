from ..handlers.inheritHandler import Base


class CustomErrorHandler(Base):
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
        super(CustomErrorHandler, self).write_resp(status_code, **kwargs)

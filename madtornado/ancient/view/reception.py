from ..handlers.inheritHandler import Base
from ..rig import register

rf = register.rf


@register.route(urls=["index", "home"])
class IndexHandler(Base):
    """

    建议将前台页面写入该模块中，该模块继承CustomErrorHandler，
    在特殊时候回遵从CustomErrorHandler定义的错误响应处理来处理错误

    CustomErrorHandler是一个举例说明，演示了如何正确的创建自己的自定义错误处理
    公共类

    """

    # @override
    async def get(self):
        self.write("<h1 style='text-align:center'>前台页面</h1>")

    # @override
    async def post(self):
        self.throw(405)

    # @override
    async def put(self):
        self.throw(405)

    # @override
    async def delete(self):
        self.throw(405)

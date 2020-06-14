from ..handlers.inheritHandler import Base
from ..rig import register


@register.route()
class AdminHandler(Base):
    """

    建议将后台管理写入该模块中，使用render注意static_url函数无法使用被madtornado禁用了，
    由于tornado静态的处理太烂了，所以内部重新实现了静态处理，如果实在需求static_url可以在
    custom/uiMethod.py中自行实现

    碎碎念::

        想要做到高并发，一定不要写成同步代码，单线程是由程序中的await进行上下文切换的，
        每一个路由都是一个协程，而这些协程中仍然可以通过gen.WaitIterator([])，gen.multi([])
        等方法进行并发，其中WaitIterator返回时无序的，multi返回是有序的，传递给multi和WaitIterator对象时，
        需要使用gen.convert_yielded将coroutine转换成Future对象再进行参数传递，或者直接传递一个包含协程的列表做参数。
        如果你想从当前协程中主动弹出可以使用gen.sleep(0)，如果程序中存在CPU密集型操作，请使用
        await IOLoop.current().run_in_executor(None, blocking_func, args)或者给阻塞函数添加@run_on_executor装饰器

    干掉阻塞代码(由于GIL关系，并不会提升太大性能，但是会减少阻塞)::

        from tornado.concurrent import run_on_executor

        import time
        import threading
        from concurrent.futures import ThreadPoolExecutor

        RecpHandler...部分
        executor = ThreadPoolExecutor(20)

        @run_on_executor
        def block_code(self):
            print(threading.current_thread())
            time.sleep(10)

    """

    # @override
    async def get(self):
        await self.render("aTorTemplate.html", mirror_page="上游传参")

    # @override
    async def post(self):
        self.throw(405)

    # @override
    async def put(self):
        self.throw(405)

    # @override
    async def delete(self):
        self.throw(405)

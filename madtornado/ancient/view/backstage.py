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
        网络非同步并发请使用gen.WaitIterator([])，这个返回是无序的，请求快先返回，有序的
        并发可使用gen.multi([])，它会等待所有并发任务都返回时返回一个任务列表，如果程序中
        实在无法避免阻塞的任务，请使用await IOLoop.current().run_in_executor(None, blocking_func, args)，
        强烈不建议。如果你不知道协程怎么工作的，建议使用同步线程的框架。传递给multi和WaitIterator对象时，
        使用gen.convert_yielded将coroutine转换成Future对象再进行参数传递，或者直接传递一个包含协程的列表做参数,
        如果你不知道coroutine和Future关系，建议了解后使用。

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
        await self.render("aTorTemplate.html", mirror_page="mirror_page")

    # @override
    async def post(self):
        self.throw(405)

    # @override
    async def put(self):
        self.throw(405)

    # @override
    async def delete(self):
        self.throw(405)

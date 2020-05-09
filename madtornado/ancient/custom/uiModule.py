from tornado.web import UIModule


class HelloModule(UIModule):

    def __init__(self, handler):
        super(HelloModule, self).__init__(handler)

    # @override
    def render(self, *args, **kwargs):
        return "<h1>Hello uiModule</h1>"


registered_class = {
    "hello_module": HelloModule
}

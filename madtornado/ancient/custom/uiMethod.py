def hello_method(self):
    return 'hello uiMethod'


def hello_func(self, content):
    return "<div>{}</h1>".format(content)


def static_url(self, path):
    """

    你可能不太了解这个重写的意义，原生tornado已经有了这个方法，如果你不知道这件事，你可以不用看我接下来说的
    为了更好的让madtornado控制静态文件，提供更好更遍历的使用，我的服务端入口中根本没有启用原生的staticFileHandler
    这样我就可以自己来控制静态文件提供更强大更易用的功能，这样导致就是static_url无法使用，但是这不是问题，你只需要
    按需要重写即可，这不是大问题，我已经提供了一小段代码，在默认配置文件中会有/s为前缀的静态管理器配置，这个返回值刚好
    契合。

    :param self: 占位，用于获取tornado对象
    :param path: 传进来的文件位置参数
    :return: 合成的文件路径

    """
    return "/s/" + path

import os

from .custom import uiMethod, uiModule
from .handlers import dealHandler
from .rig.register import register_route, end_register_route

from .boot import boot
from .conf import parser

__all__ = [
    "uiMethod", "uiModule",
    "dealHandler",
    "register_route",
]


def import_view():
    """

    动态导入view中的模块

    :return: None

    """
    exclude_file = [
        "__init__.py"
    ]
    for i in os.listdir("ancient/view"):
        if i.endswith(".py") and i not in exclude_file:
            __import__("ancient.view.{}".format(i[:-3]))


import_view()

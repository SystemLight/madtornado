from ..handlers.inheritHandler import Base

"""

logic帮助你管理全局公用逻辑，为了项目干净整洁请通过logic模块定义公用逻辑方法

"""


async def add(this: "Base"):
    this.write(str(int(this.get_argument("a")) + int(this.get_argument("b"))))

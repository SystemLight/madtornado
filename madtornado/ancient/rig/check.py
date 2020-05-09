class BaseMessage:
    """

    自定义规则函数返回的对象，可以继承该类，自定义返回Message对象

    该类是包含校验信息的消息类，当继承该类后，可以为该类添加方法

    用于得到该类时直接调用处理

    :param key: 系统调用，触发message的key值
    :param status: 状态
    :param msg: 自定义rule函数返回的自定义内容

    """

    def __init__(self, key=None, status=True, msg=None):
        self.key = key
        self.status = status
        self.msg = msg


def rule(fn):
    """

    装饰器，用于装饰自定义规则rule函数

    :param fn: 被装饰的普通函数
    :return: None

    """

    def wrap(*args, **kwargs):
        # 判断是被系统调用，还是用户调用
        if kwargs.get("caller", False):
            # 系统调用会传入caller，如果被装饰的函数接收caller会造成错误
            return fn(args[0])
        # 用户调用了规则函数，用于自定义传参，同时让返回值仍然是一个可以被系统调用函数
        return lambda param, caller: fn(param, *args, **kwargs)

    return wrap


def some(content, config):
    """

    检验dict对象，当一个key值触发错误就返回message对象

    校验字典::

        print(some({
            "name": "lisys",
            "age": None
        }, {
            "name": not_null(msg="自定义传参"),
            "age": [not_null]
        }).__dict__)

    :param content: 检验dict对象
    :param config: 配置dict对象
    :return: dict

    """
    for key in content:
        m = verify(content[key], config.get(key, []))
        if not m.status:
            m.key = key
            return m
    return BaseMessage(None, msg=content)


def every(content, config):
    """

    检验dict对象，当全部key值校验完所有规则函数返回message对象

    校验字典::

        print(every({
            "name": "lisys",
            "age": None
        }, {
            "name": not_null,
            "age": [not_null()]
        }).__dict__)

    :param content: 检验dict对象
    :param config: 配置dict对象
    :return: Message

    """
    every_message = BaseMessage(None, status=True, msg=[])
    for key in content:
        m = verify(content[key], config.get(key, []), True)
        if not m.status:
            m.key = key
            every_message.status = False
            every_message.msg.append(m)
    return every_message


def verify(param, preset, strict=False):
    """

    校验传入内容

    strict为true，并且preset是一个rule列表时，verify会校验所有rule

    并且返回一个主Message对象，该Message的msg是一个列表，包含所有的规则错误校验信息

    如果有一个规则校验失败，那么主Message对象的status值将为False

    使用预设即rule的列表进行校验::

        # 检验value的值是否符合规则，not_null为非假的规则函数，verify函数返回BaseMessage对象
        value = "hello SystemLight"
        print(verify(value, [not_null]).__dict__)

        value = "hello SystemLight"
        print(verify(value, [not_null(msg="自定义传参")]).__dict__)

    直接传入rule函数::

        value = None
        print(verify(value, not_null(msg="自定义传参")).__dict__)

        value = None
        print(verify(value, not_null).__dict__)

    :param param: 检验内容
    :param preset: 预设preset，rule函数列表，也可以直接传递rule函数
    :param strict: 是否为严格模式，即需要校验全部的rule函数才做错误返回
    :return: Message

    """
    if hasattr(preset, "__call__"):
        base_m = preset(param, caller=True)
    elif strict:
        base_m = BaseMessage(param)
        base_m.msg = []
        for rule_call in preset:
            m = rule_call(param, caller=True)
            if not m.status:
                base_m.status = False
                base_m.msg.append(m)
    else:
        for rule_call in preset:
            base_m = rule_call(param, caller=True)
            if not base_m.status:
                return base_m
        base_m = BaseMessage(param)
    return base_m


@rule
def not_null(param, msg="none"):
    """

    该rule函数是一个最简单的校验规则函数，用于校验值是否为真

    内置规则函数，校验内容是否为真值，在使用时，使用者需要按照功能自行制定规则函数

    切记规则函数需要使用@rule装饰器进行装饰，并且一定返回Message对象，使用者可以根据需求自行定制Message对象

    也可以使用默认的BaseMessage对象

    :param param: param 规则函数必须接收的值即验证的内容，类似self，用户只需接收，无须管理传入
    :param msg: msg 用户自定义传参，在调用验证函数时被使用者传入规则函数的参数
    :return: Message 所有继承BaseMessage的对象

    """
    if param:
        return BaseMessage()
    else:
        return BaseMessage(msg=msg, status=False)

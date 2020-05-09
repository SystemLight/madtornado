import json
import datetime


class DateEncoder(json.JSONEncoder):

    # @override
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class ResponseModel:
    """

    响应模型，通过实例化该类并调用该类的get方法获取返回的json格式数据
    注意，采用ResponseModel类即意味着你将不遵循restful风格规范，而
    采用madtornado风格的接口规范::

        响应码：200[使用madtornado风格的接口规范，需保证任何状态http码都为200，通过返回数据的status进行状态标记]
        返回类型示例：{"status": "fail", "description": "not found", "message": ""}

    """

    def __init__(self):
        self.status_code = 404
        self.reason = ""
        self.message = ""

    def get(self, encode_date=False):
        """

        通过改写ResponseModel实例的get方法返回值，实现全局的默认返回格式

        :param encode_date:
        :return: str

        """
        return self.dumps(self.__dict__, encode_date)

    @staticmethod
    def dumps(data, encode_date=False):
        """

        json.dumps的别名，用于方便调用

        :param data: 需要解析的数据对象
        :param encode_date: 对象中是否存在date或datetime对象
        :return: str

        """
        if encode_date:
            return json.dumps(data, cls=DateEncoder)
        else:
            return json.dumps(data)

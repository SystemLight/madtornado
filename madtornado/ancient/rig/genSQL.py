def select_tcw(table, field=("*",), where=None):
    """

    示例内容::

        select_tcw("table", ("id", "name"), where="id='2' and name='3'")
        转换sql： select id,name from table where id='2' and name='3'

    :param table: 查询的表名称
    :param field: 需要查询的字段，放入元祖中，默认值("*",)
    :param where: 筛选的内容，如 id='2' and name='3'，注意'用来声明字符串
    :return: 查询sql语句

    """
    sql = "select {} from {}".format(",".join(field), table)
    if where:
        sql += " where " + where
    return sql


def insert_tc(table, content, many=False, ph="%s"):
    """

    示例内容::

        insert_tc("table", [1, 2, 3, 4, 5])
        转换内容 ： ('insert into table values(%s,%s,%s,%s,%s)', [1, 2, 3, 4, 5])

        insert_tc("table", [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], many=True, ph="?")
        转换内容 ： ('insert into table values(?,?,?,?,?)', [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])

        insert_tc("table", {"id": 12, "name": "SystemLight"}, many=False, ph="%s")
        转换内容 ： ('insert into table(name,id) values(%s,%s)', ['SystemLight', 12])

        insert_tc("table", {"key": ["id", "name"], "value": [["1", "lisys"], ["2", "sl"]]}, many=True, ph="%s")
        转换内容 ： ('insert into table(id,name) values(%s,%s)', [['1', 'lisys'], ['2', 'sl']])

    :param table: 插入内容的表名称
    :param content: 需要插入的内容，有多种类型方式供选择
    :param many: 是否进行多行插入，默认值：False
    :param ph: 预查询模板占位符，默认值：%s
    :return: 元祖(插入预查询模板，预查询参数)

    """
    if isinstance(content, list):
        content_len = len(content[0]) if many else len(content)
        sql = "insert into {} values({})".format(table, ",".join([ph] * content_len))
    elif isinstance(content, dict):
        if many:
            field = "(" + ",".join(content["key"]) + ")"
            sql = "insert into {}{} values({})".format(table, field, ",".join([ph] * len(content["key"])))
            content = content["value"]
        else:
            field = "(" + ",".join(content.keys()) + ")"
            sql = "insert into {}{} values({})".format(table, field, ",".join([ph] * len(content.values())))
            content = list(content.values())
    else:
        raise TypeError("content is not a dict or list")
    return sql, content


def insert_update_tc(table, content, many=False, ph="%s"):
    """

    插入即更新，这条sql语句在mysql中是有效的，不同数据系统可能有所不同

    示例内容::

        insert_update_tc("table", {"id": 12, "name": "SystemLight"}, many=False, ph="%s")
        转换内容 ： ('insert into table(id,name) values(%s,%s) on duplicate key update
        id = values(id),name = values(name)', [12, 'SystemLight'])

        insert_update_tc("table", {"key": ["id", "name"], "value": [["1", "lisys"], ["2", "sl"]]}, many=True, ph="%s")
        转换内容 ： ('insert into table(id,name) values(%s,%s) on duplicate key update
        id = values(id),name = values(name)', [['1', 'lisys'], ['2', 'sl']])

    :param table: 插入即更新的table名称
    :param content: 需要插入即更新的内容，有两种类型方式供选择
    :param many: 是否进行多行插入，默认值：False
    :param ph: 预查询模板占位符，默认值：%s
    :return: 元祖(插入预查询模板，预查询参数)

    """
    if isinstance(content, dict):
        if many:
            field = "(" + ",".join(content["key"]) + ")"
            sql = "insert into {}{} values({}) on duplicate key update ".format(table, field, ",".join(
                [ph] * len(content["key"])))
            sql += ",".join(map(lambda x: "{} = values({})".format(x, x), content["key"]))
            content = content["value"]
        else:
            field = "(" + ",".join(content.keys()) + ")"
            sql = "insert into {}{} values({}) on duplicate key update ".format(table, field, ",".join(
                [ph] * len(content.values())))
            sql += ",".join(map(lambda x: "{} = values({})".format(x, x), content.keys()))
            content = list(content.values())
    else:
        raise TypeError("content is not a dict")
    return sql, content


def update_tcw(table, content, where=None, where_arg=None, ph="%s"):
    """

    生成更新sql语句

    示例内容::

        update_tcw("table", {"id": 12, "name": "SystemLight"}, ph="%s")
        转换内容 ： ('update table set name=%s,id=%s', ['SystemLight', 12])

    :param table: 更新的table名称
    :param content: 需要修改的值，字典类型
    :param where: 用于筛选，如id=2
    :param where_arg: 预查询参数，列表类型
    :param ph: 预查询模板占位符
    :return: 元祖

    """
    arg_list = list(content.values())
    sql = "update {} set {}".format(table, ",".join(map(lambda x: x + "=" + ph, content.keys())))
    if where:
        sql += " where " + where
        if where_arg:
            arg_list.extend(where_arg)
    return sql, arg_list


def delete_tw(table, where=None):
    """

    示例内容::

        delete_tw("table", where="id=1")
        转换sql： delete from table where id=1

    :param table: 需要删除的表的名称
    :param where: 用于筛选，如id=2
    :return: 删除sql

    """
    sql = "delete from {}".format(table)
    if where:
        sql += " where " + where
    return sql


def truncate_t(table):
    """

    生成清空表sql语句

    :param table: 需要清空的表的名称
    :return: ['set foreign_key_checks=0', 'truncate table tabble', 'set foreign_key_checks=1']

    """
    return ["set foreign_key_checks=0", "truncate table {}".format(table), "set foreign_key_checks=1"]


def limit(sql, start, total):
    """

    生成限制返回数量的sql语句

    :param sql: 现有sql语句
    :param start: 开始位置
    :param total: 总计条数
    :return: 附件limit的sql语句

    """
    return sql + " limit {},{}".format(start, total)


class InputResult:
    """

    该类是当数据库module执行输入语句系列时，出现错误会默认返回的错误对象

    status : 标识返回状态是否正确，如果处理sql语句时报错且回滚了数据，status标识为False

    err_info : 错误信息

    affect : sql语句影响到的行数

    last_rowid : 返回自增ID的号码

    """

    def __init__(self):
        self.status = True
        self.err_info = None
        self.affect = None
        self.last_rowid = None

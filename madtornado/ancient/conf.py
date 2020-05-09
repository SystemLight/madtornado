import configparser

# 配置文件所在路径，相对于主程序入口server.py
CONF_PATH = "config/tornado.cfg"

c_parser = configparser.ConfigParser()
c_parser.read(CONF_PATH, encoding="utf-8-sig")


class Parser:

    @staticmethod
    def options(section):
        result = {}
        for opt in c_parser.options(section):
            result[opt] = c_parser.get(section, opt)
        return result


parser = Parser()

# madtornado

[![Downloads](https://pepy.tech/badge/madtornado)](https://pepy.tech/project/madtornado)
[![version](https://img.shields.io/pypi/v/madtornado)](https://pypi.python.org/pypi/madtornado)
[![codebeat badge](https://codebeat.co/badges/da82dbdb-eceb-4166-b9e9-2d290c5f608f)](https://codebeat.co/projects/github-com-systemlight-madtornado-master)
[![Build Status](https://travis-ci.org/SystemLight/madtornado.svg?branch=master)](https://travis-ci.org/SystemLight/madtornado)
[![Documentation Status](https://readthedocs.org/projects/madtornado/badge/?version=latest)](https://madtornado.readthedocs.io/zh/latest/?badge=latest)
[![Gitter](https://badges.gitter.im/systemlight-madtornado/community.svg)](https://gitter.im/systemlight-madtornado/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

madtornado是一个tornado框架的快速构建工具   
PyPI page: https://pypi.python.org/pypi/madtornado  
[原生tornado文档参考](https://www.osgeo.cn/tornado/index.html)

# 拥有的特性

- 可以灵活配置，通过配置文件改变服务器特性，如端口等信息
- 支持装饰器注册路由，注册路由地址支持列表即可以多个不同URL指向同一个handler
- 提供代理模块，可灵活通过配置文件配置
- 提供sql语句处理模块，可简化单表查询工作。
- 提供文件分块上传案例模块，该模块非封装项只是演示如何通过madtornado完成分片上传，同时前端封装upload.js简化前端和后端交互
- 提供校验工具库check，灵活校验传递参数，配合madtornado拓展的参数获取方法可以非常容易获取和校验任何通用数据传参方式
- 提供拦截器封装模块，可以继承拦截器实现自己的拦截逻辑
- 拓展了tornado handler的方法，如果你想使用原生的tornado handler请继承RequestHandler，否则请继承handler.inheritHandler里面的Base
- 开箱即用，通过在ancient下的view中编写模块，内置两个前台和后台模块，可以自行增加或删除，也可以通过（注意需要在madtornado根目录下运行）sea -np快速创建
- 内置sea命令行工具，不仅能快速创建madtornado项目，还同时包含一些快捷操作和madtornado进行交互便于开发
- 手机端测试查找地址，通过扫控制台打印的二维码快速定位，需要配置network_index指定打印的网卡，0代表不打印二维码

# 未来计划添加特性

- 强化虚拟主机配置能力
- 增强sql模块处理能力，采用链式查找方式，更加灵活
- 增加注册路由描述功能，帮助生成网站地图时添加描述信息 

# 安装并创建一个madtornado项目

```
pip install madtornado

sea --init_project [写上你的目录路径，如./当前目录]
在当前目录下创建madtornado项目，请保证路径是空的文件夹，由于首次创建是从GitHub上进行下载，下载缓慢是有可能的，
非首次安装sea会从缓存中进行安装，如果想删除缓存使用sea --get_clean
sea --init_project ./

如果下载非常缓慢，请在release中直接下载对应版本的madtornado压缩包，放到要构建项目的目录下，
之后运行sea --init_project [路径] sea会直接解析该包，而不是去下载

查看更多sea命令
sea -h
```

# madtornado的一些特性
## 使用`Reg.check`去轻松校验传递来的表单数据
```
args = self.get_argument_for({"a": None, "b": None, "c": None})
check_rule = {
    "a": [check.not_null], "b": [check.not_null], "c": [check.not_null("c type is error")]
}
result = check.some(args, check_rule)
print(result.__dict__)
```

# 使用 madtornado

## 工作区

```
你只需要关心文件夹下，书写业务逻辑即可
%madtornado_project%\ancient\view\

例如这个模块，建议书写一些前台路由逻辑
%madtornado_project%\ancient\view\reception.py
```

## 开启服务

```
python server.py
```

## 创建一条路由

```
在该模块中 : reception.py

@register.route(use=register.PRT)
class IndexHandler(BaseHandler):
    """

    url: http://127.0.0.1:8095/prt/index

    """

    async def get(self):
        self.write("<h1 style='text-align:center'>Index</h1>")

    async def post(self):
        self.throw(404)

    async def put(self):
        self.throw(404)

    async def delete(self):
        self.throw(404)
```

## 使用sea快速创建路由

```
sea --new_recp %madtornado_project%\ancient\view\reception.py
或者使用下面的简化版，但是要在madtornado根目录下执行且reception是指定要添加路由的模块的名称
sea -nr reception
```

## 目录说明

```
通过sea命令行构建的项目会有以下内容

文件夹：
    ancient     这里是madtornado核心包，你通常的工作路径时该包内的view文件夹中，这里面的模块称为路由视图，这些模块通过装饰器注册路由
    config      madtornado是以配置为主，程序为辅的开发工具，你可以通过这里面的文件改变madtornado的一些特性，如监听端口等等
    data        这里包含一些测试用的数据，你通常不需要，如果你的项目有一些数据文件如数据库导出的内容可以放到这里面，这通常与项目有关
    log         日志文件，包含madtornado非debug模式下保存的日志，网站地图和madtornado更新日志，网站地图明确包含了路由匹配规则便于查看
    resource    资源文件，这些文件是通过程序控制进行派发访问的，不过这些控制逻辑需要你自己完成，但是madtornado提供了文件处理模块
    statics     静态文件，这些文件是通过静态处理模块直接交给用户的，如果你的文件不需要进行控制可以直接放到该文件夹下
    templates   使用模版引擎的时候，默认放置模板文件的文件夹

文件
    server.py   程序主入口，通过运行该文件来启动madtornado提供web服务吧
```

#### ancient下包说明

```
custom 自定义模板引擎方法的模块存放位置

handlers  路由核心模块，view中的路由一般会继承该包下inheritHandler中的Base类，且你可以在这里更换Base变量指向来让全局的路由更换基类

model  存放模型的位置

module  存放模块的位置，包含拓展的sql，file等操作模块

rig  存放一些额外工具的地方，其中register是路由注册模块，通过引入该模块，让路由可以被注册到路由表中

user  使用者独立的空间，你可以根据喜好放置任何内容

view  核心工作区域，你可以把所有路由写入一个模块中也可以把不同路由按照模块进行区分，内置三个模块示例均可删除，其中upload.py是大文件分块上传示例，可以直接把注册代码的注释取消掉即可使用
```

# 通过配置文件配置madtornado

```
配置文件位置：
[madtornado项目根目录]\config\tornado.cfg

配置说明：

[tornado]
release = false
frame = madtornado
frame_version = 0.3.3
project = madtornado
project_version = 0.1.0

[tornado-server]
domain =
listen = 0.0.0.0
port = 8095

[tornado-secret]
cookie_secret = madtornado
xsrf_cookies = false

[tornado-static]
url_prefix = []
path = statics/
default_filename = index.html

[tornado-template]
template_path = templates

[tornado-proxy]
xheaders = false
proxy_prefix = proxy
proxy_handler = []

[tornado-debug]
debug = true
autoreload = true
compiled_template_cache = true
static_hash_cache = true
serve_traceback = true
open_log = false

[file]
path = resource/

[token]
secret = madtornado
algorithm = HS256
over_time = 3600

[cache]
server_list = ["192.168.1.2:11211"]
over_time = 3600

[db]
max_connections = 1024
idle_seconds = 3600
wait_connection_timeout = 3
charset = utf8
host = 127.0.0.1
port = 3306
user = root
password = 111111
db = madtornado
```

# 建议

> *  Nginx ( IIS ) 使用端口 80
> *  Tomcat 使用端口 8080
> *  Apache2 使用端口 8088
> *  madtornado 使用端口 8095

# 详细文档

You can read [madtornado Documentation](https://madtornado.readthedocs.io/) online for more information.

# License

madtornado uses the MIT license, see LICENSE file for the details.
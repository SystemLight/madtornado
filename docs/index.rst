.. title:: 使用须知

===========
madtornado
===========

.. parsed-literal::
    最新版本：|release|

:Author: SystemLight
:Contact: https://github.com/SystemLight

**环境要求**: python3.5 及以上

**平台**: windows(select) | Linux(epoll)

| Madtornado is a project templates for Tornado framework and quickly generate the Tornado project.
| madtornado是一个Tornado项目开发模板，用于快速生成一个Tornado项目服务器。
| PyPI page: https://pypi.python.org/pypi/madtornado

.. Note::

    点 `star <https://github.com/SystemLight/madtornado>`_ 收藏一下

开源协议
-----------

MIT::

    The MIT License (MIT)

    Copyright (c) 2019, 2020 madtornado contributors

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

资源
-----------

* 下载源码: `戳这里下载 <https://github.com/SystemLight/madtornado/archive/master.zip>`_
* 可用版本: `戳这里查看 <https://github.com/SystemLight/madtornado/releases>`_
* GitHub: `被托管在的 GitHub <https://github.com/SystemLight/madtornado>`_

Installation
============

::

    pip install madtornado
    sea --init_project [project path]

The powerful madtornado
==============================

Very easy to check whether is not-null for arguments
------------------------------------------------------

::

    args = self.get_argument_for({"a": None, "b": None, "c": None})
    check_rule = {
        "a": [check.not_null], "b": [check.not_null], "c": [check.not_null("c type is error")]
    }
    result = check.some(args, check_rule)
    print(result.__dict__)

Used madtornado
===============

workspace
---------

::

    %madtornado_project%\ancient\view\reception.py

start server
------------

::

    python server.py

Create route
------------

::

    file : reception.py

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

Quickly create route
--------------------

::

    sea --new_recp %madtornado_project%\ancient\view\reception.py

Configure anything
==================

::

    %madtornado_project%\config\tornado.cfg

Advise
======

    -  Nginx ( IIS ) use port 80
    -  Tomcat use port 8080
    -  Apache2 use port 8088
    -  madtornado use port 8095

.. toctree::
   :maxdepth: 2
   :caption: 使用须知
   :titlesonly:

   ancient
   config
   guide

内容索引
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

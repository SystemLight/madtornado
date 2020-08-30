# madtornado | [中文文档](./README.zh.md)

`Please use madtornado4 to experience Tornado development in MVC mode`

[![Downloads](https://pepy.tech/badge/madtornado)](https://pepy.tech/project/madtornado)
[![version](https://img.shields.io/pypi/v/madtornado)](https://pypi.python.org/pypi/madtornado)
[![codebeat badge](https://codebeat.co/badges/da82dbdb-eceb-4166-b9e9-2d290c5f608f)](https://codebeat.co/projects/github-com-systemlight-madtornado-master)
[![Build Status](https://travis-ci.org/SystemLight/madtornado.svg?branch=master)](https://travis-ci.org/SystemLight/madtornado)
[![Documentation Status](https://readthedocs.org/projects/madtornado/badge/?version=stable)](https://madtornado.readthedocs.io/zh/latest/?badge=latest)
[![Gitter](https://badges.gitter.im/systemlight-madtornado/community.svg)](https://gitter.im/systemlight-madtornado/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

Madtornado is a project templates for Tornado framework and quickly generate the Tornado project.
PyPI page: https://pypi.python.org/pypi/madtornado

# Installation

```
pip install madtornado
sea --init_project [project path]
```

# The powerful madtornado
## Easily check parameters with `Reg.check` module
```
args = self.get_argument_for({"a": None, "b": None, "c": None})
check_rule = {
    "a": [check.not_null], "b": [check.not_null], "c": [check.not_null("c type is error")]
}
result = check.some(args, check_rule)
print(result.__dict__)
```

# Used madtornado

## workspace

```
%madtornado_project%\ancient\view\reception.py
```

## start server

```
python server.py
```

## Create route

```
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
```

## Quickly create route

```
sea --new_recp %madtornado_project%\ancient\view\reception.py
```

# Configure anything

```
%madtornado_project%\config\tornado.cfg
```

# Advise

> *  Nginx ( IIS ) use port 80
> *  Tomcat use port 8080
> *  Apache2 use port 8088
> *  madtornado use port 8095

# Resources

You can read [madtornado Documentation](https://madtornado.readthedocs.io/) online for more information.

# License

madtornado uses the MIT license, see LICENSE file for the details.

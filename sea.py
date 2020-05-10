import os
import re
import tqdm
import json
import shutil
import time
import zipfile
import tempfile
import platform
import argparse
import configparser
import urllib.request as u2

VERSION = "VERSION"
BUILD_NAME = "madtornado-{}".format(VERSION)
DOWNLOAD_URL = "DOWNLOAD_URL"

U_NAME = None
U_REPO = None
CH_TOKEN = None
PY_NAME = None
PY_PASSWORD = None


def init_env():
    global U_NAME, U_REPO, CH_TOKEN, U_REPO, PY_NAME, PY_PASSWORD
    U_NAME = os.getenv("U_NAME")
    U_REPO = os.getenv("U_REPO")
    CH_TOKEN = os.getenv("CH_TOKEN")
    PY_NAME = os.getenv("PY_NAME")
    PY_PASSWORD = os.getenv("PY_PASSWORD")


class TqdmUpTo(tqdm.tqdm):

    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


class InitProject:
    """

    目录说明::

        work_path -- 想要建立项目的绝对路径，即工作目录
        mad_build_path -- 构建目录绝对路径
        mad_build_zip -- 构建压缩包绝对路径
        cache_build_zip -- 全局构建目录，sea所在文件夹，用于缓存

    """

    def __init__(self, path):
        self.build_name = BUILD_NAME
        self.download_url = DOWNLOAD_URL

        self.work_path = os.path.abspath(path)
        self.mad_build_path = os.path.join(self.work_path, self.build_name)
        self.mad_build_zip = self.mad_build_path + '.zip'
        self.cache_build_zip = os.path.abspath(os.path.join(tempfile.gettempdir(), self.build_name + '.zip'))

    def run(self):
        if not os.path.isdir(self.work_path):
            os.makedirs(self.work_path)

        if not os.path.isfile(self.mad_build_zip):
            if os.path.isfile(self.cache_build_zip):
                self.local_download()
            else:
                self.download()

        self.extract()
        self.copy()
        self.clear()

    def local_download(self):
        print("local download start")
        shutil.copyfile(self.cache_build_zip, self.mad_build_zip)
        print("Path: " + self.cache_build_zip)
        print("local download end")

    def download(self):
        print("start download")
        print("Address: " + self.download_url)
        with TqdmUpTo(desc=self.build_name, ascii=True, unit='B', unit_scale=True, miniters=1) as tm:
            u2.urlretrieve(self.download_url, self.cache_build_zip, tm.update_to)
        print("Path: " + self.cache_build_zip)
        print("End download\n")
        self.local_download()

    def extract(self):
        print("Start extraction")
        build_zip = zipfile.ZipFile(self.mad_build_zip, 'r')
        build_zip.extractall(self.work_path)
        build_zip.close()
        print("Path: " + self.work_path)
        print("End extraction\n")

    def copy(self):
        print("Start copying")
        for filename in os.listdir(self.mad_build_path):
            source = os.path.join(self.mad_build_path, filename)
            target = os.path.join(self.work_path, filename)
            if os.path.isfile(source):
                print("copy file: " + source)
                shutil.copyfile(source, target)
            elif os.path.isdir(source):
                print("copy folder: " + source)
                shutil.copytree(source, target)
        print("End copy\n")

    def clear(self):
        print("Start cleaning")
        self.safe_remove(self.mad_build_zip)
        self.safe_remove(self.mad_build_path)
        print("End cleaning\n")

    @staticmethod
    def safe_remove(path):
        if os.path.isfile(path):
            os.remove(path)
        if os.path.isdir(path):
            shutil.rmtree(path)


class InitRelease:
    """

    目录说明::

        work_path -- 用户所在目录即工作目录
        sea_abs_path -- sea脚本所在的绝对路径
        setup_abs_path -- setup脚本所在的绝对路径
        mad_build_path -- 构建目录，临时存放构建目录
        mad_build_zip -- 构建目录压缩包的绝对路径
        home_path -- 用户家目录，用于临时存放pypi配置文件
        pypirc_file -- 临时.pypirc文件目录绝对路径，在家目录下

    """

    def __init__(self):
        self.version = VERSION
        self.build_name = BUILD_NAME

        self.dir_list = ["madtornado/ancient", "madtornado/config", "madtornado/data", "madtornado/log",
                         "madtornado/resource", "madtornado/statics", "madtornado/templates"]
        self.file_list = ["madtornado/server.py", ".gitignore", "README.md", "LICENSE"]

        self.work_path = os.getcwd()
        self.sea_abs_path = os.path.abspath(__file__)
        self.setup_abs_path = os.path.join(self.work_path, "setup.py")
        self.mad_build_path = os.path.join(self.work_path, self.build_name)
        self.mad_build_zip = self.mad_build_path + '.zip'
        self.home_path = os.path.expanduser('~')
        self.pypirc_file = os.path.join(self.home_path, ".pypirc")

        self.user = U_NAME
        self.repo = U_REPO
        self.git_token = CH_TOKEN
        self.py_name = PY_NAME
        self.py_password = PY_PASSWORD
        self.release_url = "https://api.github.com/repos/{}/{}/releases".format(self.user, self.repo)

        update_log = os.path.join(self.work_path, "./madtornado/log/upload.log")
        if os.path.isfile(update_log):
            with open(update_log, "r", encoding="utf-8") as desc:
                self.description = desc.read()
        else:
            self.description = ""

    def init_check(self):
        for d in self.dir_list:
            if not os.path.isdir(os.path.join(self.work_path, d)):
                return False
        for f in self.file_list:
            if not os.path.isfile(os.path.join(self.work_path, f)):
                return False
        return True

    def run(self):
        self.build_project()
        # self.change_setup()
        self.push_git_project()
        self.push_pypi_module()
        self.clean_work()

    def build_project(self):
        print("开始构建文件")
        if os.path.isdir(self.mad_build_path):
            shutil.rmtree(self.mad_build_path)
        os.mkdir(self.mad_build_path)
        for d in self.dir_list:
            source = os.path.join(self.work_path, d)
            target = os.path.join(self.mad_build_path, re.sub("^madtornado/", "", d))
            print("复制目录：" + source + " 到 " + target)
            shutil.copytree(source, target)
        for f in self.file_list:
            source = os.path.join(self.work_path, f)
            target = os.path.join(self.mad_build_path, re.sub("^madtornado/", "", f))
            print("复制文件：" + source + " 到 " + target)
            shutil.copyfile(source, target)
        with zipfile.ZipFile(self.mad_build_zip, 'w') as zip_obj:
            for file_meta in os.walk(self.mad_build_path):
                clear_path = os.path.abspath(os.path.join(self.mad_build_path, ".."))
                for file in file_meta[2]:
                    s_path = os.path.join(file_meta[0], file)
                    zip_obj.write(s_path, s_path.replace(clear_path, ""))
        print("结束构建文件\n")

    def change_setup(self):
        if os.path.isfile(self.setup_abs_path):
            with open(self.setup_abs_path, "r") as sp:
                code = sp.read()
            code = code.replace('scripts=["sea.py"],', 'scripts=["sea.py","{}"],'.format(self.build_name + ".zip"))
            with open(self.setup_abs_path, "w") as sp:
                sp.write(code)
        else:
            print("setup.py文件丢失")
            raise Exception("File lost")

    def push_git_project(self):
        print("开始上交git版本")
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/vnd.github.v3+json",
            'Authorization': "token " + self.git_token,
            'User-Agent': "PostmanRuntime/7.19.0",
        }
        data = json.dumps({
            "tag_name": self.version,
            "target_commitish": "master",
            "name": "madtornadoV" + self.version,
            "body": self.description,
            "draft": False,
            "prerelease": False
        }).encode("utf-8")
        release_req = u2.Request(self.release_url, data=data, headers=headers, method="POST")
        release_resp = u2.urlopen(release_req)
        json_page = json.loads(release_resp.read())
        upload_url = json_page["upload_url"].replace("{?name,label}", "?name=" + self.build_name + ".zip")
        print("开始提交压缩包")
        with open(self.mad_build_zip, "rb") as fd:
            file_data = fd.read()
        release_req = u2.Request(upload_url, data=file_data, headers=headers, method="POST")
        release_resp = u2.urlopen(release_req)
        json_page = json.loads(release_resp.read())
        with open(self.sea_abs_path, "r", encoding="utf-8") as fp:
            sea_code = fp.read()
        replace_str = 'DOWNLOAD_URL = "%s"' % json_page["browser_download_url"]
        new_str = re.sub('DOWNLOAD_URL\\s*=\\s*"\\s*.+\\s*"', replace_str, sea_code, 1)
        with open(self.sea_abs_path, "w", encoding="utf-8") as fp:
            fp.write(new_str)
        print("结束上交git版本\n")

    def push_pypi_module(self):
        print("开始发行pypi模块")
        with open(self.pypirc_file, "w", encoding="utf-8") as fp:
            fp.write("""[pypi]
username = {}
password = {}
""".format(self.py_name, self.py_password))
        setup_path = os.path.join(os.path.dirname(__file__), "setup.py")
        if os.path.isfile(setup_path):
            os.system("python {} bdist_wheel".format(setup_path))
            os.system("twine upload dist/*")
        else:
            print("打包配置文件丢失")
        print("结束发行pypi模块\n")

    def clean_work(self):
        print("开始清理")
        os.remove(self.mad_build_zip)
        os.remove(self.pypirc_file)
        shutil.rmtree(self.mad_build_path)
        shutil.rmtree(os.path.join(self.work_path, "dist"))
        shutil.rmtree(os.path.join(self.work_path, "build"))
        shutil.rmtree(os.path.join(self.work_path, "madtornado.egg-info"))
        print("结束清理\n")


class Sea:
    """

    目录说明::

        user_abs_path -- 用户当前所在目录绝对路径
        sea_abs_path -- sea所在目录绝对路径
        torcfg_abs_path -- sea所在目录的../config/tornado.cfg

    """

    def __init__(self):
        self.info = "Madtornado is a project templates for Tornado framework and quickly generate the Tornado project."
        self.version = VERSION
        self.arg_parse = None

        self.user_abs_path = os.getcwd()
        self.sea_abs_path = os.path.abspath(__file__)
        self.torcfg_abs_path = os.path.abspath(os.path.join(self.sea_abs_path, "../madtornado/config/tornado.cfg"))

    def run(self):
        all_parse = self.parse()
        flag = True
        for arg in all_parse:
            if all_parse[arg] and hasattr(self, arg):
                getattr(self, arg)(all_parse[arg])
                flag = False
        if flag:
            self.arg_parse.print_help()

    def parse(self):
        self.arg_parse = argparse.ArgumentParser(prog="sea", description=self.info)
        self.arg_parse.add_argument("-v", "--version", action='version', version='madtornado {}'.format(self.version))

        new_group = self.arg_parse.add_argument_group("new")
        new_group.add_argument("--new_page", nargs="?", help="create a static page")
        new_group.add_argument("--new_template", nargs="?", help="create a template page")
        new_group.add_argument("--new_view", nargs="?", help="create a view module")
        new_group.add_argument("--new_route", nargs="?", help="create a route in view")

        new_group.add_argument("-np", action="store_true", help="create a route in view")
        new_group.add_argument("-nt", action="store_true", help="create a template page")
        new_group.add_argument("-nv", action="store_true", help="create a view module")
        new_group.add_argument("-nr", nargs="?", metavar="module name", help="create a route in view")

        init_group = self.arg_parse.add_argument_group("init")
        init_group.add_argument("--init_project", nargs="?", help="Initialize a project")
        init_group.add_argument("--init_release", action="store_true", help="Prohibited")

        sync_group = self.arg_parse.add_argument_group("sync")
        sync_group.add_argument("--sync_version", action="store_true", help="Prohibited")

        get_group = self.arg_parse.add_argument_group("get")
        get_group.add_argument("--get_clean", action="store_true", help="clear cache")
        get_group.add_argument("--get_where", action="store_true", help="get path for SEA")
        get_group.add_argument("--get_nginx", action="store_true", help="download nginx for your system")
        return self.arg_parse.parse_args().__dict__

    def np(self, path):
        self.new_page(
            os.path.join(self.user_abs_path, "./statics", "index-[{}].html".format(int(time.time()))))

    def nt(self, path):
        self.new_template(
            os.path.join(self.user_abs_path, "./templates", "index-[{}].html".format(int(time.time()))))

    def nv(self, path):
        self.new_page(
            os.path.join(self.user_abs_path, "./ancient/view", "new-[{}].py".format(int(time.time()))))

    def nr(self, path):
        self.new_route(
            os.path.join(self.user_abs_path, "./ancient/view", "{}.py".format(path)))

    @staticmethod
    def new_page(arg, template=None):
        dir_path = os.path.abspath(os.path.dirname(arg))
        file_path = os.path.abspath(arg)
        if os.path.isdir(dir_path):
            if dir_path == file_path:
                print("请加入文件名称")
                return
            if os.path.isfile(file_path):
                print("文件已经存在")
                return
            if template:
                html_template = template
            else:
                html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>madtornado</title>
    <!-- -->

    <!--path:@@@路径设置口+属性-->
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x5-fullscreen" content="false">
    <meta name="full-screen" content="no">
    <meta name="apple-mobile-web-app-capable" content="no">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1,user-scalable=1"/>
    <meta name="keywords" content="关键字"/>
    <meta name="description" content="描述"/>

    <!--path:@@@路径设置口+图标-->
    <link rel="shortcut icon" href=""/>
    <link rel="bookmark" type="image/x-icon" href=""/>

    <!--path:@@@路径设置口+样式-->
    <link rel="stylesheet" type="text/css" href="">

    <!--path:@@@路径设置口+样式拓展-->
    <style>

    </style>
</head>

<body>

<!--path:@@@页面区域+头部[#header]-->
<header id="header">

</header>

<!--path:@@@页面区域+主体[#main]-->
<section id="main">

</section>

<!--path:@@@页面区域+底部[#footer]-->
<footer id="footer">

</footer>

<!--path:@@@页面区域+拓展[#aside]-->
<aside id="aside">

</aside>

<!--path:@@@路径设置口+脚本-->
<script type="application/javascript" src=""></script>

<!--path:@@@路径设置口+脚本拓展-->
<script>

</script>
</body>
</html>"""
            with open(file_path, 'w', encoding="utf8") as fp:
                fp.write(html_template)
            print(file_path + "新建完成")
        else:
            print("不是一个有效路径")

    def new_template(self, arg):
        template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <title>madtornado</title>
    <!-- -->

    <!--path:@@@路径设置口+属性-->
    <meta charset="utf-8">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x5-fullscreen" content="false">
    <meta name="full-screen" content="no">
    <meta name="apple-mobile-web-app-capable" content="no">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1,user-scalable=1"/>
    <meta name="keywords" content="关键字"/>
    <meta name="description" content="描述"/>

    <!--path:@@@路径设置口+图标-->
    <link rel="shortcut icon" href=""/>
    <link rel="bookmark" type="image/x-icon" href=""/>

    <!--path:@@@路径设置口+样式-->
    <link rel="stylesheet" type="text/css" href="">

    <!--path:@@@路径设置口+样式拓展-->
    <style>

    </style>
</head>

<body>

<!--path:@@@页面区域+头部[#header]-->
<header id="header">

</header>

<!--path:@@@页面区域+主体[#main]-->
<section id="main">

</section>

<!--path:@@@页面区域+底部[#footer]-->
<footer id="footer">

</footer>

<!--path:@@@页面区域+拓展[#aside]-->
<aside id="aside">

</aside>

<!--path:@@@路径设置口+脚本-->
<script type="application/javascript" src=""></script>

<!--path:@@@路径设置口+脚本拓展-->
<script>

</script>
</body>
</html>
"""
        self.new_page(arg, template)

    def new_view(self, arg):
        path = os.path.abspath(arg)
        with open(path, "w", encoding="utf-8") as fp:
            fp.write("""from ..handlers.baseHandler import BaseHandler
from ..rig import register""")
        self.new_route(path)

    @staticmethod
    def new_route(arg, template=None):
        path = os.path.abspath(arg)
        if os.path.isfile(path):
            if template:
                recp = template
            else:
                recp = """

@register.route(use=register.PRT)
class RouteHandler(BaseHandler):

    async def get(self):
        await self.render("aTorTemplate.html", mirror_page="<h1>前台页面</h1>")

    async def post(self):
        self.send_error(404)

    async def put(self):
        self.send_error(404)

    async def delete(self):
        self.send_error(404)

"""
            with open(path, "a", encoding="utf8") as fp:
                fp.write(recp)
            print(path + "新增完成")
        else:
            print("不是一个有效路径")

    @staticmethod
    def init_project(arg):
        ip = InitProject(arg)
        ip.run()

    def init_release(self, arg):
        if os.path.isfile(self.torcfg_abs_path) and arg:
            t_conf = configparser.ConfigParser()
            t_conf.read(self.torcfg_abs_path, encoding="utf-8-sig")
            if t_conf.getboolean("tornado", "release"):
                init_env()
                ir = InitRelease()
                if ir.init_check():
                    ir.run()
                else:
                    print("项目文件丢失，无法发行")
            else:
                print("这不是一个发行版")
        else:
            print("丢失配置文件")

    def sync_version(self, arg):
        if os.path.isfile(self.sea_abs_path) and os.path.isfile(self.torcfg_abs_path) and arg:
            with open(self.sea_abs_path, "r", encoding="utf-8") as fp:
                sea_code = fp.read()
                t_conf = configparser.ConfigParser()
                t_conf.read(self.torcfg_abs_path, encoding="utf-8-sig")
                frame_version = t_conf.get("tornado", "frame_version")
                replace_str = 'VERSION = "%s"' % frame_version
                new_str = re.sub('VERSION\\s*=\\s*"\\s*.+\\s*"', replace_str, sea_code, 1)
            with open(self.sea_abs_path, "w", encoding="utf-8") as fp:
                fp.write(new_str)
            print("同步版本成功")
        else:
            print("丢失配置文件")

    def get_nginx(self, arg):
        if platform.system() == "Windows":
            url_path = "http://nginx.org/download/nginx-1.16.1.zip"
        else:
            url_path = "http://nginx.org/download/nginx-1.16.1.tar.gz"
        nginx_path = os.path.join(self.user_abs_path, url_path.split("/")[-1])
        print("start download")
        print("Address: " + url_path)
        with TqdmUpTo(desc="nginx", ascii=True, unit='B', unit_scale=True, miniters=1) as tm:
            u2.urlretrieve(url_path, nginx_path, tm.update_to)
        print("Path: " + nginx_path)
        print("End download\n")

    @staticmethod
    def get_where(arg):
        print(os.path.abspath(__file__))

    @staticmethod
    def get_clean(arg):
        ip = InitProject("./")
        ip.clear()
        ip.safe_remove(ip.cache_build_zip)


def main():
    s = Sea()
    s.run()


if __name__ == "__main__":
    main()

import configparser
from setuptools import setup

# 配置文件路径常量
TORNADO_CONF = "./madtornado/config/tornado.cfg"
README = "README.rst"
REQUIREMENTS = "requirements.txt"

# 解析配置文件
parser = configparser.ConfigParser()
parser.read(TORNADO_CONF, encoding="utf-8-sig")
with open(README, "r", encoding="utf-8") as fp:
    long_description = fp.read()
with open(REQUIREMENTS, "r", encoding="utf-8") as fp:
    install_requires = list(map(lambda x: x.strip("\n"), fp.readlines()))

# 生成setup配置项
setup(
    python_requires=">=3.5",
    name="madtornado",
    version=parser.get("tornado", "frame_version"),
    author="SystemLight",
    author_email="1466335092@qq.com",
    maintainer="SystemLight",
    maintainer_email="1466335092@qq.com",
    url="https://github.com/SystemLight/madtornado",
    license="MIT",
    description="Madtornado is a project templates for Tornado framework and quickly generate the Tornado project.",
    long_description=long_description,
    download_url="https://github.com/SystemLight/madtornado/releases",
    install_requires=install_requires,
    extras_require={},
    tests_require=[],
    setup_requires=[],
    dependency_links=[],
    platforms=["Windows", "Linux"],
    keywords=[
        "tornado", "web", "http_server", "mt", "Mad_tornado", "madtornado",
        "Tornado project template", "python3", "sea", "generate the Tornado project",
        "tornado cli", "tornado脚手架", "生成tornado项目"
    ],
    include_package_data=True,
    package_dir={},
    packages=[],
    package_data={},
    data_files=[],
    ext_modules=[],
    py_modules=["sea"],
    scripts=["sea.py"],
    entry_points={
        'console_scripts': [
            'sea = sea:main'
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)

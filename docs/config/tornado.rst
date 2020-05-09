``tornado.cfg`` --- 服务配置
========================================================================================

配置文件说明::

    [tornado]
    release = false
    frame = madtornado
    frame_version = 0.3.1
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

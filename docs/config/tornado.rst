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
    ; url_prefix拥有多种形态，
    ; 1. 增加多个可访问前缀 ["\s","\v"]，这样在URL中/s和/r都会映射到静态目录中，默认静态目录是path参数配置
    ; 2. 如果前缀映射的目录不同，可以这样配置[["\s","other/statics/"],"\v"]
    ; 3. 当然有时默认文件也不同，可以这样配置[["\s","other/statics/","main.html"],"\v"]
    ; 4. madtornadoV0.3.8版本加入了SPA配置，如果开启前端路由模式，必须指定一个spa页面，所有路由交给这个页面
    ; 5. 如果spa模式默认是不开启的，如果只想给某个映射静态路由添加spa_pag，这样配置
    ; [["\s","other/statics/","main.html","spa_page.html"],"\v"]
    ; 6. madtornado接收到请求时如果没找到任何内容会去请求静态页面，如果没有请求到静态页面且没有开启spa模式将返回404
    ; 7. 404返回内容可以重写，重写方法参考inheritHandler/CustomErrorBaseHandler并且交给staticHandler继承
    url_prefix = []
    path = statics/
    default_filename = index.html
    spa_page =

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

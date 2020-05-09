from ..conf import parser

import memcache

import json

option = parser.options("cache")
print("[syncMemcached] is imported.\n")


class Component:

    def __init__(self):
        self.memcachedClient = None
        self.over_time = option["over_time"]
        self.server_list = json.loads(option["server_list"])

    def __enter__(self):
        self.on()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.off()

    def __getitem__(self, item):
        return self.memcachedClient.get(item)

    def __setitem__(self, key, value):
        return self.memcachedClient.set(key, value, self.over_time)

    def __delitem__(self, key):
        return self.memcachedClient.delete(key)

    def on(self) -> None:
        self.memcachedClient = memcache.Client(self.server_list, debug=False)

    def off(self) -> None:
        if self.memcachedClient:
            self.memcachedClient.disconnect_all()
            self.memcachedClient = None

    def spe_set(self, key: str, value: str, over_time: int) -> int:
        return self.memcachedClient.set(key, value, over_time)

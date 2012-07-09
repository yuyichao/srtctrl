# coding=utf-8

class DefaultInit:
    def __init__(self, conn):
        self._conn = conn
        self._initialized = False
    def got_pkg(self):
        pass

iface.initializer.default = DefaultInit

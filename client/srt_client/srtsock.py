import os, ctypes
from socket import * # for flags only

from .srtbase import *

_hdl = ctypes.CDLL(None)

def _init():
    _hdl.recv.argtypes = (ctypes.c_int, ctypes.c_void_p,
                          ctypes.c_size_t, ctypes.c_int)
    _hdl.recv.restype = ctypes.c_ssize_t
    _hdl.send.argtypes = (ctypes.c_int, ctypes.c_void_p,
                          ctypes.c_size_t, ctypes.c_int)
    _hdl.send.restype = ctypes.c_ssize_t

def recv(fd, count, flags=0):
    buff = ctypes.create_string_buffer(count)
    rcount = _hdl.recv(fd, buff, count, flags)
    return buff.raw[:rcount]

def send(fd, buff, flags=0):
    rcount = _hdl.send(fd, buff, len(buff), flags)
    return rcount

_init()
del _init

from gi.repository import Gio, GLib

class SrtSock(SrtBase):
    # conf={} is included in here just in case some configuration is needed in
    # the future
    def __init__(self, conf={}):
        super().__init__(conf=conf)
        self._client = Gio.SocketClient()
        self._conn = None
    @classmethod
    def new_from_fd(klass, fd, conf={}):
        self = klass(conf={})
        try:
            _socket = Gio.Socket.new_from_fd(fd)
        except GLib.GError:
            return
        self._conn = _socket.connection_factory_create_connection()

    def is_connected(self):
        if self._conn is None:
            return False
        connected = self._conn.is_connected()
        if connected:
            return True
        self._conn = None
    def get_fd(self):
        if not self.is_connected():
            return -1
        return self._conn.get_socket().get_fd()

    # connection
    def conn_async(self, host, port, cb, *args):
        if self.is_connected():
            return
        self._client.connect_to_host_async(host, port, None,
                                           self._conn_cb, (cb, args))
    def conn(self, host, port, cb, *args):
        if self.is_connected():
            return
        try:
            self._conn = self._client.connect_to_host(host, port, None)
        except GLib.GError:
            self._conn = None
    def _conn_cb(self, client, res, data):
        cb, args = data
        try:
            self._conn = client.connect_to_host_finish(res)
        except GLib.GError:
            self._conn = None
        try:
            cb(self, *args)
        except TypeError:
            pass
    def disconn(self):
        if not self.is_connected():
            return
        self._conn.close(None)
        self._conn = None
    def disconn_async(self, cb, *args):
        if not self.is_connected():
            return
        self._conn.close_async(0, None, self._disconn_cb, (cb, args))
    def _disconn_cb(self, client, res, data):
        cb, args = data
        client.close_finish(res)
        try:
            cb(self, *args)
        except TypeError:
            pass

    def send(self, buff):
        pass
    def recv(self, count):
        pass

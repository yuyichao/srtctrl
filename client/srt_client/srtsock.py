#   Copyright (C) 2012~2012 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, ctypes, fcntl
from socket import * # for flags only
import locale
locale.setlocale(locale.LC_ALL, '')

from .srtbase import *

_hdl = ctypes.CDLL(None, use_errno=True)

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
    if rcount < 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
    return buff.raw[:rcount]

def send(fd, buff, flags=0):
    rcount = _hdl.send(fd, buff, len(buff), flags)
    if rcount < 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
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
        self._send_buff = b''
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
        self._send_buff = b''
        self._client.connect_to_host_async(host, port, None,
                                           self._conn_cb, (cb, args))
    def conn(self, host, port):
        if self.is_connected():
            return
        self._send_buff = b''
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
        self._send_buff = b''
        try:
            cb(self, *args)
        except TypeError:
            pass
    def disconn(self):
        if not self.is_connected():
            return
        self._conn.close(None)
        self._conn = None
        self._send_buff = b''
    def disconn_async(self, cb, *args):
        if not self.is_connected():
            return
        self._conn.close_async(0, None, self._disconn_cb, (cb, args))
    def _disconn_cb(self, client, res, data):
        cb, args = data
        client.close_finish(res)
        self._conn = None
        self._send_buff = b''
        try:
            cb(self, *args)
        except TypeError:
            pass

    def _set_non_block(self):
        fd = self.get_fd()
        if fd < 0:
            return
        try:
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        except OSError as err:
            # k, if EINTR happens I should have reraise the exception~
            return
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
    def _send(self, buff, flags=0):
        self._set_non_block()
        return send(self.get_fd(), buff, flags=flags)
    def _recv(self, count, flags=0):
        self._set_non_block()
        return recv(self.get_fd(), count, flags=flags)
    def _try_send_buff(self):
        try:
            c = self._send(self._send_buff)
        except OSError:
            pass

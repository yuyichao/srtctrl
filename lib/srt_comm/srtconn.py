# coding=utf-8

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

from gi.repository import SrtSock as _sock, Gio, GLib, GObject
from srt_comm.srtaddr import *
from srt_comm import util

class SrtConn(_sock.Sock):
    __gsignals__ = {
        "package": (GObject.SignalFlags.RUN_FIRST,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_STRING,))
    }
    def __init__(self, sfamily=None, stype=None, sprotocol=None, fd=None,
                 **kwargs):
        if not fd is None:
            kwargs['fd'] = fd
        if not sfamily is None:
            kwargs['family'] = sfamily
        if not stype is None:
            kwargs['type'] = stype
        if not sprotocol is None:
            kwargs['protocol'] = sprotocol
        super().__init__(**kwargs)
        self._buffer = ''
        self.connect('receive', __class__._receive_cb)
    @staticmethod
    def _receive_cb(self, obj):
        self._buffer += _sock.buff_from_obj(obj).decode('utf-8')
        while True:
            package, self._buffer = self._do_dispatch(self._buffer)
            if package:
                self.emit('package', package)
            else:
                break
    def _do_dispatch(self, buff):
        # To be overloaded
        return (buff, '')
    def recv(self):
        while True:
            newbuf = super().recv(65536)
            if not newbuf:
                return
            self._buffer += newbuf.decode('utf-8')
            package, self._buffer = self._do_dispatch(self._buffer)
            if len(package):
                return package
    def send(self, buff):
        try:
            buff = buff.encode('utf-8')
        except AttributeError:
            pass
        return super().send(buff)
    def conn(self, addr):
        family = self.get_family()
        addrs = get_sock_addrs(addr, family)
        err = None
        for addr in addrs:
            try:
                if super().conn(addr):
                    return True
            except GLib.GError as error:
                err = error
        if not err is None:
            raise err
        return False
    @staticmethod
    def _conn_cb(conn, res, args):
        (self, addrs, cb, args) = args
        try:
            res = self.conn_finish(res)
        except GLib.GError:
            res = False
        if res:
            util.call_cb(cb, True, *args)
            return
        __class__._conn_get_addrs_cb(self, addrs, cb, args)
    @staticmethod
    def _conn_get_addrs_cb(addrs, self, cb, *args):
        try:
            if len(addrs) == 0:
                util.call_cb(cb, False, *args)
        except TypeError:
            util.call_cb(cb, False, *args)
        if super(__class__, self).conn_async(addrs[0], __class__._conn_cb,
                                             (self, addrs[1:], cb, args)):
            return
        __class__._conn_get_addrs_cb(self, addrs[1:], cb, *args)
    def conn_async(self, addr, cb, *args):
        get_sock_addrs_async(addr, self.get_family(),
                             __class__._conn_get_addrs_cb, self, cb, *args)
    @staticmethod
    def _conn_recv_cb(success, self, cb, *args):
        res = False
        if success:
            try:
                res = self.start_recv()
            except GLib.GError:
                pass
        util.call_cb(cb, res, *args)
    def conn_recv(self, addr, cb, *args):
        self.conn_async(addr, __class__._conn_recv_cb, self, cb, *args)
    @staticmethod
    def _real_bind(self, addrs):
        err = None
        for addr in addrs:
            try:
                if super().bind(addr, True):
                    return True
            except GLib.GError as error:
                err = error
        if not err is None:
            raise err
        return False
    def bind(self, addr):
        family = self.get_family()
        addrs = get_sock_addrs(addr, family)
        return __class__._real_bind(self, addrs)
    @staticmethod
    def _bind_get_addrs_cb(addrs, self, cb, *args):
        res = False
        try:
            res = __class__._real_bind(self, addrs)
        except GLib.GError:
            pass
        util.call_cb(cb, res, *args)
    def bind_async(self, addr, cb, *args):
        get_sock_addrs_async(addr, self.get_family(),
                             __class__._bind_get_addrs_cb, self, cb, *args)
    @staticmethod
    def _bind_accept_cb(success, self, cb, *args):
        res = False
        if success:
            try:
                res = self.start_accept()
            except GLib.GError:
                pass
        util.call_cb(cb, res, *args)
    def bind_accept(self, addr, cb, *args):
        self.bind_async(addr, __class__._bind_accept_cb, self, cb, *args)

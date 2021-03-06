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

from __future__ import print_function, division
from gi.repository import SrtSock as _sock, Gio, GLib, GObject
from .srtaddr import *
from . import util

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
        super(SrtConn, self).__init__(**kwargs)
        self._buffer = ''
        self._byte_buff = b''
        self.connect('receive', SrtConn._receive_cb)
    def _decode(self, byte_buff):
        self._byte_buff += byte_buff
        # well this is the simplist way I know to create a empty unicode string
        # in both python2 and python3
        buff = b''.decode()
        while True:
            try:
                buff += self._byte_buff.decode('utf-8')
                self._byte_buff = b''
                return buff
            except UnicodeDecodeError as error:
                (valid, invalid, left) = (
                    self._byte_buff[:error.start],
                    self._byte_buff[error.start:error.end],
                    self._byte_buff[error.end:])
                try:
                    buff += valid.decode('utf-8')
                except:
                    pass
                if left:
                    self._byte_buff = left
                    continue
                self._byte_buff = invalid
                return buff
    @staticmethod
    def _receive_cb(self, obj):
        self._buffer += self._decode(_sock.buff_from_obj(obj))
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
            package, self._buffer = self._do_dispatch(self._buffer)
            if len(package):
                return package
            newbuf = super(SrtConn, self).recv(65536)
            if not newbuf:
                return
            self._buffer += self._decode(newbuf)
    def send(self, buff):
        # util.printp(repr(buff))
        try:
            buff = buff.encode('utf-8')
        except:
            pass
        return super(SrtConn, self).send(buff)
    def conn(self, addr):
        family = self.get_family()
        addrs = get_sock_addrs(addr, family)
        err = None
        for addr in addrs:
            try:
                if super(SrtConn, self).conn(addr):
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
            util.call_catch(cb, True, *args)
            return
        SrtConn._conn_get_addrs_cb(addrs, self, cb, *args)
    @staticmethod
    def _conn_get_addrs_cb(addrs, self, cb, *args):
        try:
            if len(addrs) == 0:
                util.call_catch(cb, False, *args)
                return
        except TypeError:
            util.call_catch(cb, False, *args)
            return
        if super(SrtConn, self).conn_async(addrs[0], SrtConn._conn_cb,
                                           (self, addrs[1:], cb, args)):
            return
        SrtConn._conn_get_addrs_cb(addrs[1:], self, cb, *args)
    def conn_async(self, addr, cb, *args):
        get_sock_addrs_async(addr, self.get_family(),
                             SrtConn._conn_get_addrs_cb, self, cb, *args)
    @staticmethod
    def _conn_recv_cb(success, self, cb, *args):
        res = False
        if success:
            try:
                res = self.start_recv()
            except GLib.GError:
                pass
        util.call_catch(cb, res, *args)
    def conn_recv(self, addr, cb, *args):
        self.conn_async(addr, SrtConn._conn_recv_cb, self, cb, *args)
    @staticmethod
    def _real_bind(self, addrs):
        err = None
        for addr in addrs:
            try:
                if super(SrtConn, self).bind(addr, True):
                    return True
            except GLib.GError as error:
                err = error
        if not err is None:
            raise err
        return False
    def bind(self, addr):
        family = self.get_family()
        addrs = get_sock_addrs(addr, family)
        return SrtConn._real_bind(self, addrs)
    @staticmethod
    def _bind_get_addrs_cb(addrs, self, cb, *args):
        res = False
        try:
            res = SrtConn._real_bind(self, addrs)
        except GLib.GError:
            pass
        util.call_catch(cb, res, *args)
    def bind_async(self, addr, cb, *args):
        get_sock_addrs_async(addr, self.get_family(),
                             SrtConn._bind_get_addrs_cb, self, cb, *args)
    @staticmethod
    def _bind_accept_cb(success, self, cb, *args):
        res = False
        if success:
            try:
                res = self.start_accept()
            except GLib.GError:
                pass
        util.call_catch(cb, res, *args)
    def bind_accept(self, addr, cb, *args):
        self.bind_async(addr, SrtConn._bind_accept_cb, self, cb, *args)

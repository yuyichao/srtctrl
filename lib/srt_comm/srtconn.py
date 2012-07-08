# coding=utf-8

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
        self.connect('receive', SrtConn._receive_cb)
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
            if newbuf is None:
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
    def _conn_cb(self, conn, res, args):
        (addrs, cb, args) = args
        try:
            res = self.conn_finish(res)
        except GLib.GError:
            res = False
        if res:
            util.call_cb(cb, True, *args)
            return
        self._conn_get_addrs_cb(addrs, cb, args)
    def _conn_get_addrs_cb(self, addrs, cb, *args):
        try:
            if len(addrs) == 0:
                util.call_cb(cb, False, *args)
        except TypeError:
            util.call_cb(cb, False, *args)
        if super().conn_async(addrs[0], self._conn_cb, (addrs[1:], cb, args)):
            return
        self._conn_get_addrs_cb(addrs[1:], cb, *args)
    def conn_async(self, addr, cb, *args):
        get_sock_addrs_async(addr, self.get_family(), self._conn_get_addrs_cb,
                             cb, *args)
    def _conn_recv_cb(self, success, cb, *args):
        res = False
        if success:
            try:
                res = self.start_recv()
            except GLib.GError:
                pass
        util.call_cb(cb, res, *args)
    def conn_recv(self, addr, cb, *args):
        self.conn_async(addr, self._conn_recv_cb, cb, *args)
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
        self._real_bind(addrs)
    def _bind_get_addrs_cb(self, addrs, cb, *args):
        res = False
        try:
            res = self._real_bind(addrs)
        except GLib.GError:
            pass
        util.call_cb(cb, res, *args)
    def bind_async(self, addr, cb, *args):
        get_sock_addrs_async(addr, self.get_family(), self._bind_get_addrs_cb,
                             cb, *args)
    def _bind_accept_cb(self, success, cb, *args):
        res = False
        if success:
            try:
                res = self.start_accept()
            except GLib.GError:
                pass
        util.call_cb(cb, res, *args)
    def bind_accept(self, addr, cb, *args):
        self.bind_async(addr, self._bind_accept_cb, cb, *args)

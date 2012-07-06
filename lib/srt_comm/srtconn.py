# coding=utf-8

from gi.repository import SrtSock as _sock, Gio, GLib, GObject
from srt_comm.srtaddr import *

class SrtConn(_sock.Sock):
    __gsignals__ = {
        "package": (GObject.SignalFlags.RUN_FIRST,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_STRING,))
    }
    def __init__(self, sfamily=None, stype=None, sprotocol=None, fd=None):
        super().__init__()
        if not fd is None:
            res = super().init_from_fd(fd)
            if not res:
                raise IOError
        else:
            if sfamily is None:
                sfamily = Gio.SocketFamily.IPV4
            if stype is None:
                stype = Gio.SocketType.STREAM
            if sprotocol is None:
                sprotocol = Gio.SocketProtocol.DEFAULT
            res = super().init(sfamily, stype, sprotocol)
            if not res:
                raise IOError
        self._buffer = b''
        self.connect('receive', self._receive_cb)
    def _receive_cb(self, obj):
        self._buffer += _sock.buff_from_obj(obj).decode('utf-8')
        package, self._buffer = self._do_dispatch(self._buffer)
        self.emit('package', package)
    def _do_dispatch(self, buff):
        # To be overloaded
        return (buff, '')
    def recv(self):
        while True:
            newbuf = super().recv(65536)
            if newbuf is None:
                return
            self._buffer += newbuf
            package, self._buffer = self._do_dispatch(self._buffer)
            if len(package):
                return package
    def conn(self, addr):
        family = self.get_family()
        addrs = get_sock_addrs(addr, family)
        err = None
        for addr in addrs:
            try:
                if super().conn(addr):
                    return True
            except GLib.GError as err:
                pass
        if not err is None:
            raise err
        return False
    def _conn_cb(self, res, args):
        (addrs, cb, args) = args
        try:
            res = self.conn_finish(res)
        except GLib.GError:
            res = False
        if res:
            cb(True, *args)
            return
        self._conn_get_addrs_cb(addrs, cb, args)
    def _conn_get_addrs_cb(self, addrs, cb, *args):
        try:
            if len(addr) == 0:
                cb(False, *args)
        except TypeError:
            cb(False, *args)
        if super().conn_async(addrs[0], self._conn_cb, (addrs[1:], cb, args)):
            return
        self._conn_get_addrs_cb(addrs[1:], cb, *args)
    def conn_async(self, addr, cb, *args):
        get_sock_addrs_async(addr, self.get_family(), self._conn_get_addrs_cb,
                             cb, *args)
    def conn_and_recv(self):
        pass
    def bind(self, addr):
        family = self.get_family()
        addrs = get_sock_addrs(addr, family)
        err = None
        for addr in addrs:
            try:
                if super().bind(addr, True):
                    return True
            except GLib.GError as err:
                pass
        if not err is None:
            raise err
        return False
    def bind_async(self):
        pass
    def bind_accept(self):
        pass

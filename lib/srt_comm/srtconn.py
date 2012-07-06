# coding=utf-8

from gi.repository import SrtSock as _sock, Gio

def _unix_sock_addr(addr):
    if addr.startswith('\0'):
        addr = addr[1:].encode('utf-8')
        addr = Gio.UnixSocketAddress.new_with_type(
            addr, Gio.UnixSocketAddressType.ABSTRACT)
        return addr
    else:
        addr = Gio.UnixSocketAddress.new(addr)
        return addr

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
            self._buffer += super().recv(65536)
            package, self._buffer = self._do_dispatch(self._buffer)
            if len(package):
                return package
    def _conn_unix(self, addr):
        addr = _unix_sock_ddr(addr)
        super().conn(addr)
    def _conn_inet(self):
        pass
    def conn(self, addr):
        family = self.get_family()
        if family == Gio.SocketFamily.UNIX:
            self._conn_unix(addr)
            return True
        elif family in [Gio.SocketFamily.INET, Gio.SocketFamily.INET6]:
            self._conn_inet(addr)
            return True
        return False
    def conn_async(self):
        pass
    def conn_and_recv(self):
        pass

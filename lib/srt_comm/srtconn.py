# coding=utf-8

from gi.repository import SrtSock as _sock

class SrtConn(_sock.Sock):
    __gsignals__ = {
        "package": (GObject.SignalFlags.RUN_FIRST,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_STRING,))
    }
    def __init__(self, sfamily=None, stype=None, sprotocol=None, fd=None):
        super().__init__()
        if not fd is None:
            super().init_from_fd(fd)
            return
        if sfamily is None:
            sfamily = Gio.SocketFamily.IPV4
        if stype is None:
            stype = Gio.SocketType.STREAM
        if sprotocol is None:
            sprotocol = Gio.SocketProtocol.DEFAULT
        super().init(sfamily, stype, sprotocol)
        self._buffer = b''
        self.connect('receive', self._receive_cb)
    def _receive_cb(self, obj):
        self._buffer += _sock.buff_from_obj(obj).decode('utf-8')
        package, self._buffer = self._do_dispatch(self._buffer)
        self.emit('package', package)
    def _do_dispatch(self, buff):
        return (buff, '')
    def recv(self):
        while True:
            self._buffer += super().recv(65536)
            package, self._buffer = self._do_dispatch(self._buffer)
            if len(package):
                return package

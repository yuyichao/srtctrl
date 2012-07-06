# coding=utf-8

from gi.repository import SrtSock as _sock

class SrtConn(_sock.Sock):
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

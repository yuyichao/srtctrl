# coding=utf-8

from gi.repository import SrtSock as _sock

class SrtConn(_sock.Sock):
    def __init__(self):
        super().__init__()

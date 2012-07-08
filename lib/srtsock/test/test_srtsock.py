#!/usr/bin/env python
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

import os
from gi.repository import SrtSock, Gio, GLib

n_children = 5
port = 15000

childrenleft = n_children
disconnected = {}

mainloop = GLib.MainLoop()

def find_addr():
    rslvr = Gio.Resolver.get_default()
    addrs = rslvr.lookup_by_name('localhost', None)
    for addr in addrs:
        if addr.get_family() == Gio.SocketFamily.IPV4:
            return Gio.InetSocketAddress.new(addr, port)

def start_children():
    for i in range(n_children * 2):
        os.system("python test_srtchild.py %d %d &" % (port, i))

def disconn_cb(sock):
    print(sock, " Disconnected (parent)")
    if not id(sock) in disconnected:
        disconnected[id(sock)] = sock
        global childrenleft
        childrenleft -= 1
    if childrenleft <= 0:
        mainloop.quit()

def recv_cb(self, obj, buff):
    buff['buff'] += SrtSock.buff_from_obj(obj)
    print(buff['buff'])
    if b'EXIT' in buff['buff']:
        print('exit')
        disconn_cb(self)

def accept_cb(sock, nsock):
    nsock.connect('receive', recv_cb, {'buff': b''})
    nsock.connect('disconn', disconn_cb)
    nsock.start_recv()

def start_mainloop(sock):
    sock.start_accept()
    sock.connect('accept', accept_cb)
    mainloop.run()

def main():
    sock = SrtSock.Sock.new(Gio.SocketFamily.IPV4, Gio.SocketType.STREAM,
                            Gio.SocketProtocol.DEFAULT)
    addr = find_addr()
    sock.bind(addr, True)
    start_children()
    for i in range(n_children):
        nsock = sock.accept()
        import time
        time.sleep(.1)
        print(nsock.recv(100))
        nsock.close()
    start_mainloop(sock)
    sock.close()

if __name__ == '__main__':
    main()

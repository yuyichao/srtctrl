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

from __future__ import print_function, division
import os, sys, time

if os.fork():
    exit()

(port, i) = sys.argv[1:]
port = int(port)
_id = int(i)

from gi.repository import SrtSock, Gio, GLib

mainloop = GLib.MainLoop()

def find_addr():
    rslvr = Gio.Resolver.get_default()
    addrs = rslvr.lookup_by_name('localhost', None)
    for addr in addrs:
        if addr.get_family() == Gio.SocketFamily.IPV4:
            return Gio.InetSocketAddress.new(addr, port)

time.sleep(.5)

sock = SrtSock.Sock.new(Gio.SocketFamily.IPV4, Gio.SocketType.STREAM,
                        Gio.SocketProtocol.TCP)
addr = find_addr()
sock.conn(addr)
sock.send(b'asdf\n')
sock.send(b'asdf\n')
sock.send(b'asdf\n')
sock.send(b'EXIT')

def timeout_cb(sock):
    print('timeout')
    sock.send(b'EXIT')
    return True

def disconn_cb(sock):
    print(sock, " Disconnected (child)")
    mainloop.quit()

def do_send(sock, i):
    if False:
        print('sync')
        sock.wait_send()
    else:
        print('async')
        sock.start_send()
        sock.connect('disconn', disconn_cb)
        GLib.timeout_add_seconds(2, timeout_cb, sock)
        mainloop.run()

do_send(sock, _id)
sock.close()

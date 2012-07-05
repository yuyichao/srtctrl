#!/usr/bin/env python

import os, sys, time

if os.fork():
    exit()

(port, i) = sys.argv[1:]
port = int(port)
i = int(i)

from gi.repository import SrtSock, Gio, GLib

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
print('sent')
sock.wait_send()
sock.close()

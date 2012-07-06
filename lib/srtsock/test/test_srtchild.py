#!/usr/bin/env python

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

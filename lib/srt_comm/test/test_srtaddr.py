#!/usr/bin/env python

from srt_comm import *
from gi.repository import GLib, Gio

print(get_sock_addrs('google.com:80', Gio.SocketFamily.IPV4))
print(get_sock_addrs('google.com:80', Gio.SocketFamily.IPV6))
print(get_sock_addrs(('google.com', 80),
                     Gio.SocketFamily.IPV4))
print(get_sock_addrs(('google.com', 80),
                     Gio.SocketFamily.IPV6))
print(get_sock_addrs('google.com', Gio.SocketFamily.UNIX))

print("sync->async")

get_sock_addrs_async('google.com:80', Gio.SocketFamily.IPV4, print)
get_sock_addrs_async('google.com:80', Gio.SocketFamily.IPV6, print)
get_sock_addrs_async(('google.com', 80),
                     Gio.SocketFamily.IPV4, print)
get_sock_addrs_async(('google.com', 80),
                     Gio.SocketFamily.IPV6, print)
get_sock_addrs_async('google.com', Gio.SocketFamily.UNIX, print)

mainloop = GLib.MainLoop()

GLib.timeout_add_seconds(1, lambda: mainloop.quit())
mainloop.run()

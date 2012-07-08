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

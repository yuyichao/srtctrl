# coding=utf-8

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
from gi.repository import Gio, GLib
from . import util

def _unix_sock_addr(addr):
    if addr.startswith('\0'):
        addr = addr[1:].encode('utf-8')
        addr = Gio.UnixSocketAddress.new_with_type(
            addr, Gio.UnixSocketAddressType.ABSTRACT)
        return addr
    else:
        addr = Gio.UnixSocketAddress.new(addr)
        return addr

def _unix_sock_addr_async(addr, cb, *args):
    addr = _unix_sock_addr(addr)
    GLib.idle_add(util.call_cb, cb, [addr], *args)

def _std_inet_addr(addr):
    try:
        host, port = addr
    except ValueError:
        i = addr.rindex(':')
        host = addr[:i]
        port = addr[i + 1:]
    port = int(port)
    return host, port

def _inet_addrs(host):
    resolver = Gio.Resolver.get_default()
    return resolver.lookup_by_name(host, None)

def _inet_sock_addrs(addr, family):
    host, port = _std_inet_addr(addr)
    resolver = Gio.Resolver.get_default()
    addrs = resolver.lookup_by_name(host, None)
    res = []
    for addr in addrs:
        if addr.get_family() == family:
            res.append(Gio.InetSocketAddress.new(addr, port))
    return res

def _inet_sock_addrs_cb(resolver, res, args):
    (port, family, cb, args) = args
    try:
        addrs = resolver.lookup_by_name_finish(res)
    except GLib.GError:
        addrs = []
    res = []
    for addr in addrs:
        if addr.get_family() == family:
            res.append(Gio.InetSocketAddress.new(addr, port))
    util.call_cb(cb, res, *args)

def _inet_sock_addrs_async(addr, family, cb, *args):
    host, port = _std_inet_addr(addr)
    resolver = Gio.Resolver.get_default()
    resolver.lookup_by_name_async(host, None,
                                  _inet_sock_addrs_cb, (port, family, cb, args))

def get_sock_addrs(addr, family):
    if family == Gio.SocketFamily.UNIX:
        return [_unix_sock_addr(addr)]
    elif family in [Gio.SocketFamily.IPV4, Gio.SocketFamily.IPV6]:
        return _inet_sock_addrs(addr, family)
    return []

def get_sock_addrs_async(addr, family, cb, *args):
    if family == Gio.SocketFamily.UNIX:
        _unix_sock_addr_async(addr, cb, *args)
    elif family in [Gio.SocketFamily.IPV4, Gio.SocketFamily.IPV6]:
        _inet_sock_addrs_async(addr, family, cb, *args)
    else:
        GLib.idle_add(util.call_cb, cb, [], *args)

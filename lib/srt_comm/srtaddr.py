# coding=utf-8

from gi.repository import Gio, GLib
from srt_comm import util

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

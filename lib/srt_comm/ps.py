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

import os, socket, ctypes
from srt_comm.util import *
from srt_comm.srtconn import SrtConn
from gi.repository import GObject
import fcntl

_fds_env_name = 'SRT_PASSED_FDS'

def fork_ps(cb, *args):
    pid = os.fork()
    # will this ever happen (in python)? Or will it be a exception?.....
    if pid < 0:
        return False
    elif pid:
        # parent
        (pid, status) = os.waitpid(pid, 0)
        if status:
            return False
        return True
    else:
        # child
        try:
            gpid = os.fork()
        except OSError:
            os._exit(1)
        if gpid < 0:
            os._exit(1)
        elif gpid:
            os._exit(0)
        else:
            try:
                cb(*args)
            except Exception as err:
                print(err)
                os._exit(1)
            os._exit(0)

def _exec_fd_cb(fname, args, fds):
    os.environ[_fds_env_name] = ' '.join([str(fd) for fd in fds])
    os.execvp(fname, args)

def exec_with_fd(fname, args=None, fds=[]):
    fds = [int(fd) for fd in fds]
    for fd in fds:
        flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, flags & ~fcntl.FD_CLOEXEC)
    if args is None:
        args = [fname]
    else:
        args = [str(arg) for arg in args]
    return fork_ps(_exec_fd_cb, fname, args, fds)

def get_passed_fds():
    fds = read_env(_fds_env_name, default='')
    fds = [try_to_int(fd) for fd in fds.split()]
    return [fd for fd in fds if not fd is None]

_self_hdl = ctypes.CDLL(None, use_errno=True)
def sock_pair(domain=socket.AF_UNIX, type=socket.SOCK_STREAM, protocol=0):
    ary = (ctypes.c_int * 2)()
    if _self_hdl.socketpair(domain, type, protocol, ctypes.byref(ary)) < 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))
    return (ary[0], ary[1])

def sock_pair_n(n=1, domain=socket.AF_UNIX, type=socket.SOCK_STREAM, protocol=0):
    pairs = []
    for i in range(n):
        pairs += [sock_pair(domain, type, protocol)]
    return tuple(zip(*pairs))

def conn_pair(domain=socket.AF_UNIX, type=socket.SOCK_STREAM, protocol=0,
              gtype=SrtConn):
    return tuple(GObject.new(gtype, fd=fd)
                 for fd in sock_pair(domain, type, protocol))

def conn_pair_n(n=1, domain=socket.AF_UNIX, type=socket.SOCK_STREAM, protocol=0,
                gtype=SrtConn):
    pairs = []
    for i in range(n):
        pairs += [conn_pair(domain, type, protocol, gtype)]
    return tuple(zip(*pairs))

def exec_n_conn(fname, n=1, args=None, gtype=SrtConn):
    pconn, cconn = conn_pair_n(n=n, gtype=gtype)
    for conn in pconn:
        flags = fcntl.fcntl(conn.props.fd, fcntl.F_GETFD)
        fcntl.fcntl(conn.props.fd, fcntl.F_SETFD, flags | fcntl.FD_CLOEXEC)
    if exec_with_fd(fname, args=args, fds=[conn.props.fd for conn in cconn]):
        return pconn

def get_passed_conns(gtype=SrtConn):
    return tuple(GObject.new(gtype, fd=fd) for fd in get_passed_fds())
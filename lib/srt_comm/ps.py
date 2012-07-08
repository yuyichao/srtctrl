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

import os

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
            except:
                os._exit(1)
            os._exit(0)

def _exec_fd_cb(fname, args, fds):
    os.environ[_fds_env_name] = ' '.join([str(fd) for fd in fds])
    os.execvp(fname, args)

def exec_with_fd(fname, args=None, fds=[]):
    fds = [int(fd) for fd in fds]
    if args is None:
        args = [fname]
    else:
        args = [str(arg) for arg in args]
    return fork_ps(_exec_fd_cb, fname, args, fds)

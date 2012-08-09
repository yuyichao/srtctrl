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
import sys
from srt_comm import *
from os import path

def main():
    import srt_slave
    sys.argv.pop(0)
    sync = sys.argv.pop(0)
    fname = sys.argv[0]
    if sync.lower() == 'false':
        sync = False
    else:
        sync = True
    conn = get_passed_conns(gtype=JSONSock)[0]
    iface = srt_slave.new_iface(conn, sync)
    if sync:
        iface.wait_ready()
        iface.lock(wait=True)
    try:
        execfile(fname)
    except:
        print_except()

def start_slave(host, pwd, fname=None, args=[], sync=True, **kw):
    if not isstr(fname):
        return False
    fname = path.abspath(path.join(pwd, fname))
    if (isstr(args) or isnum(args)):
        args = [str(args)]
    else:
        try:
            args = [str(arg) for arg in args]
        except:
            return False
    sync = str(bool(sync))
    conn = exec_n_conn(sys.executable,
                       args=[sys.executable, __file__, sync, fname] + args,
                       n=1, gtype=JSONSock)[0]
    return host.add_slave_from_jsonsock(conn)

if __name__ == '__main__':
    main()
elif 'setiface' in globals():
    setiface.slave.python = start_slave

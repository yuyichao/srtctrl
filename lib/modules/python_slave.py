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

import sys
from srt_comm import *

def main():
    pass

def start_slave(host, fname=None, **kw):
    if fname is None:
        return False
    fname = str(fname)
    conn = exec_n_conn(sys.executable,
                       args=[sys.executable, __file__, fname],
                       n=1, gtype=JSONSock)[0]
    return host.add_slave_from_jsonsock(self, sock)

if __name__ == '__main__':
    main()
else:
    iface.slave.python = start_slave

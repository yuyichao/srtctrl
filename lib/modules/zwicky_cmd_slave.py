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
import time as _time

def try_get_time(line):
    try:
        tstr, rest = line.split(None, 1)
    except:
        return 0, rest
    try:
        t = guess_interval(tstr)
        return t, rest
    except:
        pass

def sep_line(line):
    pass

def exec_line(iface, line):
    if line.startswith('#') or line.startswith('*') or not line:
        return
    printy(line)

def main():
    from srt_slave import default
    fname = sys.argv[1]
    fh = open(fname, 'r')
    for line in fh:
        exec_line(default, line.strip(' \n\r\t\b:'))

def start_zwicky_cmd(host, pwd, fname=None, **kw):
    if not isstr(fname):
        return False
    fname = path.abspath(path.join(pwd, fname))
    getiface.slave.python(host, pwd, fname=__file__, args=[fname], **kw)

if __name__ == '__main__':
    main()
elif 'setiface' in globals():
    setiface.slave.zwicky_cmd = start_zwicky_cmd

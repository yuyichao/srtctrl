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

def exec_line(iface, line):
    printy(line)

def main():
    from srt_slave import default
    fname = sys.argv[1]
    fh = open(fname, 'r')
    for line in fh:
        exec_line(default, line.strip())

def start_zwicky_cmd(host, pwd, fname=None, **kw):
    if not isstr(fname):
        return False
    fname = path.abspath(path.join(pwd, fname))
    getiface.slave.python(host, pwd, fname=__file__, args=[fname], **kw)

if __name__ == '__main__':
    main()
elif 'setiface' in globals():
    setiface.slave.zwicky_cmd = start_zwicky_cmd

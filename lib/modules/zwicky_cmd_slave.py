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

def get_func(iface, cmd):
    if cmd.lower() == 'record':
        return iface.record
    return iface.cmd[cmd]

def exec_cmd(iface, cmd, args, kwargs):
    if not cmd:
        return
    func = get_func(iface, cmd)
    func(*args, **kwargs)

def exec_line(iface, line):
    t, cmd, args, kwargs = parse_line(line)
    if t is None or t <= 0:
        exec_cmd(iface, cmd, args, kwargs)
        return
    if not cmd:
        wait_main(t)
        return
    if cmd == 'radio':
        rad_args = args
        rad_kwargs = kwargs
        cmd = ''
        args = []
        kwargs = {}
    else:
        rad_arg = ''
    t += _time.time()
    while t >= _time.time():
        exec_cmd(iface, 'radio', rad_args, rad_kwargs)
    exec_cmd(iface, cmd, args, kwargs)

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

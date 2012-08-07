#!/usr/bin/env python
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

from __future__ import print_function, division, unicode_literals
from srt_comm import *
from gi.repository import GLib
import sys
import random

try:
    conn = get_passed_conns()[0]
    send = True
except:
    conn = exec_n_conn(sys.executable,
                       args=[sys.executable, __file__], n=1)[0]
    send = False

printg(conn)

base_str = "随便挑的字符串\n"
rep_times = 10

printr(repr(base_str))

def get_dirty_utf8():
    invalid_bytes = b'\xaf\xb0\x8e\x9f\xff\xe8\xca\xe4'
    res = b''
    for i in range(len(base_str)):
        res += base_str[i].encode('utf-8') + invalid_bytes[i:i + 1]
    return res

def get_pkgs():
    full = get_dirty_utf8() * rep_times
    last_pos = 0
    pkgs = []
    for i in range(1, len(full) - 1):
        if not random.randint(0, 3):
            pkgs.append(full[last_pos: i])
            last_pos = i
    pkgs.append(full[last_pos: len(full)])
    return pkgs

if send:
    pkgs = get_pkgs()
    for pkg in pkgs:
        conn.send(pkg)
        conn.wait_send()
else:
    buff = ''
    while True:
        new_buff = conn.recv()
        if new_buff is None:
            break
        buff += new_buff
        printg(buff)
        print()
    printbg(buff)
    printbg(repr(get_dirty_utf8()))

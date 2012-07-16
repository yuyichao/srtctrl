#!/usr/bin/env python

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
from srt_comm import *
from gi.repository import GLib
import os

n_children = 5
port = 15004

childrenleft = n_children
disconnected = {}

mainloop = GLib.MainLoop()

def start_children():
    for i in range(n_children):
        os.system("python test_jsonchild2.py %d %d &" % (port, i))

def disconn_cb(conn):
    print(conn, " Disconnected (parent)")
    if not id(conn) in disconnected:
        disconnected[id(conn)] = conn
        global childrenleft
        childrenleft -= 1
    if childrenleft <= 0:
        mainloop.quit()

def timeout_cb(conn):
    print('timeout')
    conn.send({"type": "EXIT"})
    return True

def accept_cb(conn, nconn):
    nconn.connect('disconn', disconn_cb)
    nconn.start_send()
    GLib.timeout_add_seconds(1, timeout_cb, nconn)
    nconn.send({"type": "EXIT"})

def start_mainloop(conn):
    conn.connect('accept', accept_cb)
    mainloop.run()

def start_accept_cb(*args):
    print(args)

def main():
    conn = JSONSock()
    conn.bind_accept(('localhost', port), start_accept_cb)
    start_children()
    start_mainloop(conn)
    conn.close()

if __name__ == '__main__':
    main()

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
from gi.repository import GLib, Gio
import os

n_children = 5
port = 15001

childrenleft = n_children
disconnected = {}

mainloop = GLib.MainLoop()

def start_children():
    for i in range(n_children * 2):
        os.system("python test_srtchild.py %d %d &" % (port, i))

def disconn_cb(conn):
    print(conn, " Disconnected (parent)")
    if not id(conn) in disconnected:
        disconnected[id(conn)] = conn
        global childrenleft
        childrenleft -= 1
    if childrenleft <= 0:
        mainloop.quit()

def recv_cb(self, msg, buff):
    buff['buff'] += msg
    print(repr(buff['buff']))
    if 'EXIT' in buff['buff']:
        print('exit')
        disconn_cb(self)

def accept_cb(conn, nconn):
    nconn.connect('package', recv_cb, {'buff': ''})
    nconn.connect('disconn', disconn_cb)
    nconn.start_recv()

def start_mainloop(conn):
    conn.start_accept()
    conn.connect('accept', accept_cb)
    mainloop.run()

def main():
    conn = SrtConn()
    conn.bind(('localhost', port))
    start_children()
    for i in range(n_children):
        nconn = conn.accept()
        import time
        time.sleep(.1)
        print(nconn)
        print(nconn.recv())
        nconn.close()
    start_mainloop(conn)
    conn.close()

if __name__ == '__main__':
    main()

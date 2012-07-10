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

import os, sys, time

if os.fork():
    exit()

(port, i) = sys.argv[1:]
port = int(port)
_id = int(i)

from gi.repository import Gio, GLib
from srt_comm import *

mainloop = GLib.MainLoop()

time.sleep(.5)

conn = JSONSock()
conn.conn(('localhost', port))
conn.send({"type": "nothing"})
conn.send({"type": "nothing"})
conn.send({"type": "nothing"})
conn.send({"type": "EXIT"})

def timeout_cb(conn):
    print('timeout')
    conn.send({"type": "EXIT"})
    return True

def disconn_cb(conn):
    print(conn, " Disconnected (child)")
    mainloop.quit()

def do_send(conn, i):
    if i % 2:
        print('sync')
        conn.wait_send()
    else:
        print('async')
        conn.start_send()
        conn.connect('disconn', disconn_cb)
        GLib.timeout_add_seconds(2, timeout_cb, conn)
        mainloop.run()

do_send(conn, _id)
conn.close()

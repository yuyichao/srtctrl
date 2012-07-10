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

from srt_comm import *

conn = exec_n_conn('./test_jsonchild3.py', n=1, gtype=JSONSock)[0]

print(conn)

mainloop = GLib.MainLoop()

def timeout_cb(conn):
    print('timeout')
    conn.send({"type": 'EXIT'})
    return True

def disconn_cb(conn):
    print('parent exit.')
    mainloop.quit()

conn.connect('disconn', disconn_cb)
conn.start_send()
GLib.timeout_add_seconds(1, timeout_cb, conn)
conn.send({"type": 'EXIT'})

mainloop.run()

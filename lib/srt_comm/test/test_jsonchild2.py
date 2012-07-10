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

from gi.repository import GLib
from srt_comm import *

mainloop = GLib.MainLoop()

time.sleep(.5)
def recv_cb(self, msg):
    print(repr(msg))
    if 'EXIT' == msg['type']:
        print('exit')
        mainloop.quit()

conn = JSONSock()
conn.conn_recv(('localhost', port), None)
conn.connect('got-obj', recv_cb)

mainloop.run()

conn.close()

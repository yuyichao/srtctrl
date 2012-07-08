#!/usr/bin/env python

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
def recv_cb(self, msg, buff):
    buff['buff'] += msg
    print(repr(buff['buff']))
    if 'EXIT' in buff['buff']:
        print('exit')
        mainloop.quit()

conn = SrtConn()
conn.conn_recv(('localhost', port), None)
conn.connect('package', recv_cb, {'buff': ''})

mainloop.run()

conn.close()

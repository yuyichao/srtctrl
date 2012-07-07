#!/usr/bin/env python

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

conn = SrtConn()
conn.conn(('localhost', port))
conn.send('asdf\n')
conn.send('asdf\n')
conn.send('asdf\n')
conn.send('EXIT')

def timeout_cb(conn):
    print('timeout')
    conn.send('EXIT')
    return True

def disconn_cb(conn):
    print(conn, " Disconnected (child)")
    mainloop.quit()

def do_send(conn, i):
    if False:
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

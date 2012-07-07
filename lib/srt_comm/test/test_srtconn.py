#!/usr/bin/env python

from srt_comm import *
from gi.repository import GLib, Gio
import os

n_children = 5
port = 15000

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

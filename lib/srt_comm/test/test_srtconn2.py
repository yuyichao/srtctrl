#!/usr/bin/env python

from srt_comm import *
from gi.repository import GLib, Gio
import os

n_children = 5
port = 15001

childrenleft = n_children
disconnected = {}

mainloop = GLib.MainLoop()

def start_children():
    for i in range(n_children):
        os.system("python test_srtchild2.py %d %d &" % (port, i))

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
    conn.connect('accept', accept_cb)
    mainloop.run()

def start_accept_cb(*args):
    print(args)

def main():
    conn = SrtConn()
    conn.bind_accept(('localhost', port), start_accept_cb)
    start_children()
    start_mainloop(conn)
    conn.close()

if __name__ == '__main__':
    main()

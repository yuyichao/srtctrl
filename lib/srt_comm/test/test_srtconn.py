#!/usr/bin/env python

from srt_comm import *
from gi.repository import GLib, Gio

n_children = 5
port = 15000

childrenleft = n_children
disconnected = {}

mainloop = GLib.MainLoop()

def start_children():
    for i in range(n_children * 2):
        os.system("python test_srtchild.py %d %d &" % (port, i))

def disconn_cb(sock):
    print(sock, " Disconnected (parent)")
    if not id(sock) in disconnected:
        disconnected[id(sock)] = sock
        global childrenleft
        childrenleft -= 1
    if childrenleft <= 0:
        mainloop.quit()

def recv_cb(self, msg, buff):
    buff['buff'] += msg
    print(buff['buff'])
    if b'EXIT' in buff['buff']:
        print('exit')
        disconn_cb(self)

def accept_cb(sock, nsock):
    nsock.connect('package', recv_cb, {'buff': ''})
    nsock.connect('disconn', disconn_cb)
    nsock.start_recv()

def start_mainloop(sock):
    sock.start_accept()
    sock.connect('accept', accept_cb)
    mainloop.run()

def main():
    srtconn = SrtConn()
    srtconn.bind(('localhost', port))
    start_children()
    for i in range(n_children):
        nsock = srtconn.accept()
        import time
        time.sleep(.1)
        print(nsock.recv())
        nsock.close()
    start_mainloop(srtconn)
    srtconn.close()

if __name__ == '__main__':
    main()

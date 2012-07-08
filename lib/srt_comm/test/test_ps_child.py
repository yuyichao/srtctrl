#!/usr/bin/env python

from srt_comm import *

conn = get_passed_conns()[0]

print(conn)

mainloop = GLib.MainLoop()

def recv_cb(self, msg, buff):
    buff['buff'] += msg
    print(repr(buff['buff']))
    if 'EXIT' in buff['buff']:
        print('exit')
        mainloop.quit()

conn.start_recv()
conn.connect('package', recv_cb, {'buff': ''})

mainloop.run()

conn.close()

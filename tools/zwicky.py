#!/usr/bin/env python

# coding=utf-8

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
from gi.repository import GObject, GLib, Gio
import sys
import random
import time

fakedata = [52, 67, 115, 230, 449, 751, 1203, 1687, 2104, 2342, 2568,
            2469, 2496, 2339, 2387, 2306, 2399, 2502, 2487, 2530, 2523,
            2400, 2414, 2343, 2389, 2367, 2544, 2575, 2502, 2498, 2517,
            2470, 2506, 2435, 2493, 2506, 2501, 2549, 2503, 2416, 2395,
            2334, 2384, 2409, 2455, 2414, 2440, 2440, 2411, 2399, 2313,
            2290, 2406, 2513, 2609, 2416, 2059, 1737, 1338, 793, 446,
            233, 115, 65]

class ZwickyFakeServer:
    def __init__(self, conn):
        self._conn = conn
        self._conn.start_send()
        self._conn.start_recv()
        self._conn._do_dispatch = self.dispatch
        self._conn.connect("package", self._pkg_cb)
        self._conn.connect("disconn", self._quit)
        self._mainloop = GLib.MainLoop()
        self._h_c = 0
        self._v_c = 0
        self._source_on = False
    def run(self):
        self._mainloop.run()
    def dispatch(self, buff):
        return get_line(buff)[1:3]
    def _quit(self, conn):
        self._mainloop.quit()
    def _pkg_cb(self, conn, pkg):
        if pkg.lower().startswith('gotit'):
            return
        if pkg.lower().startswith('bye'):
            conn.close()
            return
        reply = None
        try:
            reply = self._handle_pkg(pkg)
        except:
            print_except()
        if reply is None:
            conn.send("-1\n")
        else:
            conn.send(reply)
    def _handle_pkg(self, pkg):
        if pkg.lower().startswith("rubusy"):
            if random.randint(0, 1):
                return "NO take a turn\n"
            else:
                return "MAYBE try again later\n"
            return
        elif pkg.startswith("move"):
            seq = pkg.split()
            direct = int(seq[1])
            count = int(seq[2])
            if direct in [6, 7]:
                if direct == 6:
                    self._source_on = False
                if direct == 7:
                    self._source_on = True
                return "C 0 %d 0 %d\n" % (direct, random.randint(1, 9999))
            if not 0 <= direct <= 3 or count <= 0:
                return
            if direct == 1:
                if self._h_c + count >= 2000:
                    rcount = 2000 - self._h_c
                    self._h_c = 2000
                else:
                    rcount = count + random.randint(0, 1)
                    self._h_c += rcount
            elif direct == 0:
                if self._h_c - count <= 0:
                    rcount = self._h_c
                    self._h_c = 0
                else:
                    rcount = count + random.randint(0, 1)
                    self._h_c -= rcount
            elif direct == 3:
                if self._v_c + count >= 1000:
                    rcount = 1000 - self._v_c
                    self._v_c = 1000
                else:
                    rcount = count + random.randint(0, 1)
                    self._v_c += rcount
            elif direct == 2:
                if self._v_c - count <= 0:
                    rcount = self._v_c
                    self._v_c = 0
                else:
                    rcount = count + random.randint(0, 1)
                    self._v_c -= rcount
            time.sleep(rcount / 50)
            if rcount < count:
                return ("T %d %d %d %d\n" %
                        (rcount, direct, count, random.randint(1, 9999)))
            else:
                return ("M %d %d %d %d\n" %
                        (count, rcount - count,
                         direct, random.randint(1, 9999)))
        elif pkg.startswith("radio"):
            if self._source_on:
                r = 2
            else:
                r = 1
            time.sleep(1)
            return "128 %s %d\n" % (" ".join([str(d * r +
                                                  random.randint(-100, 100))
                                              for d in fakedata]),
                                    random.randint(1, 9999))

def main():
    conn = get_passed_conns()[0]
    printg("Client Connected")
    server = ZwickyFakeServer(conn)
    try:
        server.run()
    except:
        print_except()
    printg("Client Quit")

if __name__ == "__main__":
    main()

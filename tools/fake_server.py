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

__mainloop__ = GLib.MainLoop()
def bind_cb(res):
    if res:
        printbg("Listening now.")
    else:
        __mainloop__.quit()

def accept_cb(conn, nconn):
    exec_with_fd(sys.executable, [sys.executable, "zwicky.py"],
                 [nconn.props.fd])

def main():
    conn = SrtConn()
    conn.bind_accept("0.0.0.0:1421", bind_cb)
    conn.connect("accept", accept_cb)
    try:
        __mainloop__.run()
    except:
        print_except()

if __name__ == "__main__":
    main()

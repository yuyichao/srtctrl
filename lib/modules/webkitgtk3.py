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
from os import path
import sys, os

def main():
    import srt_slave, srt_wkgtk
    from gi.repository import GLib, Gtk, GObject
    uri = sys.argv[1]
    try:
        os.chdir(sys.argv[2])
    except:
        pass
    conn = get_passed_conns(gtype=JSONSock)[0]
    iface = srt_slave.new_iface(conn, False)
    # TODO
    iface.slave.connect("quit", Gtk.main_quit)
    ui = srt_wkgtk.SrtUI(uri, {"IFace": iface})
    ui.show_all()
    Gtk.main()

def start_webkitgtk3(host, pwd, uri="", **kw):
    if not uri:
        raise ValueError("Need The URL of the webpage to load.")
    if not pwd:
        pwd = os.getcwd()
    else:
        pwd = str(pwd)
    conn = exec_n_conn(sys.executable,
                       args=[sys.executable, __file__, uri, pwd],
                       n=1, gtype=JSONSock)[0]
    # conn.connect("disconn", lambda conn: host.emit("quit"))
    return host.add_slave_from_jsonsock(conn)

if __name__ == '__main__':
    main()
elif 'setiface' in globals():
    setiface.slave.webkitgtk3 = start_webkitgtk3

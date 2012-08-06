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

from __future__ import print_function, division
from srt_client import *
from srt_comm import *

from os import path
dirname = path.dirname(path.abspath(__file__))

def err_cb(center, errno, msg):
    print(msg)

def get_obj_cb(sock, pkg):
    printr("get_obj_cb", pkg)

def main():
    srtcenter = SrtCenter({"generic": {"host": "yyc-arch.org"}})
    srtcenter.connect('error', err_cb)
    host, slave = conn_pair(gtype=JSONSock)
    srtcenter.add_slave_from_jsonsock(host)
    srtcenter.create_slave_by_name("python",
                                   {"fname": "%s/test_slave.py" % dirname})
    slave.start_recv()
    slave.start_send()
    slave.connect("got-obj", get_obj_cb)
    srtcenter.run()

if __name__ == '__main__':
    main()

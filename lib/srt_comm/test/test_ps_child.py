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
from srt_comm import *

conn = get_passed_conns()[0]

print(conn)

def recv_cb(self, msg, buff):
    buff['buff'] += msg
    print(repr(buff['buff']))
    if 'EXIT' in buff['buff']:
        print('exit')
        srt_main_quit()

conn.start_recv()
conn.connect('package', recv_cb, {'buff': ''})

srt_main()

conn.close()

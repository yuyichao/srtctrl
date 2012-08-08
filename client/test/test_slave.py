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

import time

printbg("TEST SLAVE")
try:
    printb("RES:", iface.cmd.move("galacti", offset=[30, 40]))
except:
    print_except()
printb("RES:", iface.cmd.move("galactic", offset=[30, 40]))
printb("config", iface.config.zwicky.station)
iface.config.zwicky.station = [10, 10, 10]
printb("RES:", iface.cmd.set_freq(1420.8, 1))
printb("RES:", iface.cmd.calib(1))
printb("RES:", iface.cmd.move(args=[40, 30]))
t = iface.make_time("10s")
while not iface.time_passed(t):
    printb("RES:", iface.cmd.radio())
printb("RES:", iface.cmd.reset())
printbg("TEST QUIT")
iface.quit()

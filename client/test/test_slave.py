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
from srt_slave.default import *

printbg("TEST SLAVE")
try:
    printb("RES:", cmd.move("galacti", offset=[30, 40]))
except InvalidRequest:
    print_except()
printb("RES:", cmd.move("galactic", offset=[30, 40]))
printb("config", config.zwicky.station)
config.zwicky.station = [10, 10, 10]
printb("RES:", cmd.set_freq(1420.8, 1))
printb("RES:", cmd.calib(1))
printb("RES:", cmd.move(args=[40, 30]))
t = make_time("10s")
while not time_passed(t):
    printb("RES:", cmd.radio())
printb("RES:", cmd.reset())
printbg("TEST QUIT")
quit()

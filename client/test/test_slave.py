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

print("TEST SLAVE")
printr("RES:", iface.cmd.move(offset=[0, 10]))
printr("RES:", iface.cmd.calib(2))
printr("RES:", iface.cmd.move(args=[0, 48]))
t = iface.make_time("20s")
while not iface.time_passed(t):
    printr("RES:", iface.cmd.radio())
printr("RES:", iface.cmd.reset())
print("TEST QUIT")
iface.quit()

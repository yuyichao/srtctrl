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
from math import *
from srt_comm import *

DIRECT_HDEC = 0
DIRECT_HINC = 1
DIRECT_DOWN = 2
DIRECT_UP = 3

class ZwickyMoter:
    def __init__(self, zwicky):
        self._zwicky = zwicky
        for key in ["az_lim", "el_lim", "az_c_per_deg", "el_c_per_deg",
                    "pushrod", "rod_l1", "rod_l2", "rod_l3", "rod_t0",
                    "rod_crate", "poffset"]:
            self._zwicky.get_config(key)
        self.configs = self._zwicky.configs
        self._zwicky.connect("alarm::timer", self._timer_cb)
        self.reset()
    def _timer_cb(self, zwicky, name, nid, args):
        if zwicky.cmd_busy:
            return
        self.pos_chk()
    def reset(self):
        self._az_c = 0
        self._el_c = 0
        self._az_set = -10
        self._el_set = -10
        self._az_edge = -1
        self._el_edge = -1
        self.move_signal()
    def move(self, direct, count, edge):
        if direct == DIRECT_HDEC:
            self._az_edge = 0
            self._az_c -= count
        elif direct == DIRECT_HINC:
            self._az_edge = 0
            self._az_c += count
        elif direct == DIRECT_DOWN:
            self._el_edge = 0
            self._el_c -= count
        elif direct == DIRECT_UP:
            self._el_edge = 0
            self._el_c += count

        if edge == DIRECT_HDEC:
            self._az_edge = -1
        elif edge == DIRECT_HINC:
            self._az_edge = 1
        elif edge == DIRECT_DOWN:
            self._el_edge = -1
        elif edge == DIRECT_UP:
            self._el_edge = 1

        if self._az_c < 0 or edge == DIRECT_HDEC:
            self._az_c = 0
        if self._el_c < 0 or edge == DIRECT_DOWN:
            self._el_c = 0
        self.move_signal()
    def __getattr__(self, key):
        if key == "az":
            return self.az_c2d(self._az_c)
        elif key == "el":
            return self.el_c2d(self._el_c)
        elif key == "az_c_set":
            return int(self.az_d2c(self._az_set))
        elif key == "el_c_set":
            return int(self.el_d2c(self._el_set))
        else:
            raise AttributeError(key)
    def move_signal(self):
        self._zwicky.send_signal("move", [self.az, self.el])
    def l_rod(self, degree=None):
        if degree == None:
            degree = self.configs.el_lim[0]
        l2 = (self.configs.rod_l1**2 + self.configs.rod_l2**2
              - self.configs.rod_l3**2
              - 2 * self.configs.rod_l1 * self.configs.rod_l2
              * cos((self.configs.rod_t0 - degree) * (pi / 180)))
        return sqrt(l2 if l2 > 0 else 0)
    def degree_at_l(self, l_rod):
        if l_rod < 0:
            l_rod = 0
        l2 = l_rod**2 + self.configs.rod_l3**2
        c = ((self.configs.rod_l1**2 + self.configs.rod_l2**2 - l2) /
             (2 * self.configs.rod_l1 * self.configs.rod_l2))
        if c > 1:
            c = 1
        if c < -1:
            c = -1
        return self.configs.rod_t0 - acos(c) * (180 / pi)
    def az_c2d(self, count):
        degree = count / self.configs.az_c_per_deg + self.configs.az_lim[0]
        degree -= self.configs.poffset[0]
        if degree > self.configs.az_lim[1]:
            return self.configs.az_lim[1]
        return degree
    def el_c2d(self, count):
        if self.configs.pushrod:
            L0 = self.l_rod()
            degree = self.degree_at_l(L0 - count / self.configs.rod_crate)
        else:
            degree = count / self.configs.el_c_per_deg + self.configs.el_lim[0]
        degree -= self.configs.poffset[1]
        if degree > self.configs.el_lim[1]:
            return self.configs.el_lim[1]
        return degree

    def az_chk(self, degree):
        if degree < self.configs.az_lim[0]:
            degree = self.configs.az_lim[0]
        if degree > self.configs.az_lim[1]:
            return self.configs.az_lim[1]
        return degree
    def az_d2c(self, degree):
        degree = self.az_chk(degree + self.configs.poffset[0])
        return (degree - self.configs.az_lim[0]) * self.configs.az_c_per_deg
    def el_chk(self, degree):
        if degree > self.configs.el_lim[1] or degree > 90:
            return degree > self.configs.el_lim[1]
        if degree < self.configs.el_lim[0] or degree < -90:
            return self.configs.el_lim[0]
        return degree
    def el_d2c(self, degree):
        degree = self.el_chk(degree + self.configs.poffset[1])
        if self.configs.pushrod:
            L0 = self.l_rod()
            L1 = self.l_rod(degree)
            return int(round((L0 - L1) * self.configs.rod_crate))
        else:
            return (degree - self.configs.el_lim[0]) * self.configs.el_c_per_deg

    def pos_chk(self):
        if self._zwicky.remote_busy:
            return
        if self.el_c_set > self._el_c and not self._el_edge == 1:
            self._zwicky.send_move(DIRECT_UP, self.el_c_set - self._el_c)
        if self.az_c_set > self._az_c and not self._az_edge == 1:
            self._zwicky.send_move(DIRECT_HINC, self.az_c_set - self._az_c)
        if self.az_c_set < self._az_c and not self._az_edge == -1:
            self._zwicky.send_move(DIRECT_HDEC, self._az_c - self.az_c_set)
        if self.el_c_set < self._el_c and not self._el_edge == -1:
            self._zwicky.send_move(DIRECT_DOWN, self._el_c - self.el_c_set)
    def set_pos(self, az, el):
        self._az_set = float(az)
        self._el_set = float(el)
        self.pos_chk()
    def get_offset(self):
        return self.configs.poffset[:2]

setiface.device.zwicky.motor = ZwickyMoter

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

class ZwickyMoter:
    def __init__(self, zwicky):
        self._zwicky = zwicky
        for key in ["az_lim", "el_lim", "az_c_per_deg", "el_c_per_deg",
                    "pushrod", "rod_l1", "rod_l2", "rod_l3", "rod_t0",
                    "rod_crate"]:
            self._zwicky.get_config(key)
    def reset(self):
        self._az_c = 0
        self._el_c = 0

iface.zwicky.motor = ZwickyMoter

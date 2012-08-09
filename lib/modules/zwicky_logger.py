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
import time as _time

class ZwickyLogger:
    def __init__(self, iface, logger):
        self._iface = iface
        self._logger = logger
        self._iface.connect("res", self._res_cb)
        self._iface.connect("log", self._log_cb)
        self._format = ('{time_str} {az} {el} {azoff} {eloff} '
                        '{gala_l} {gala_b} {calib} {sys_tmp} '
                        '{minfreq} {maxfreq} {nfreq} {data}')
        self._time_format = "%Y:%j:%H:%M:%S"
        self._gmt_time = True
    def _write_radio(self, data, **props):
        try:
            time_t = props["time"]
            if self._gmt_time:
                time_struct = _time.gmtime(time_t)
            else:
                time_struct = _time.localtime(time_t)
            props["time_str"] = _time.strftime(self._time_format, time_struct)
        except:
            print_except()
        try:
            props["az"], props["el"] = props["pos"]
        except:
            print_except()
        try:
            props["azoff"], props["eloff"] = props["offset"]
        except:
            print_except()
        try:
            props["gala_l"], props["gala_b"] = props["gala_pos"]
        except:
            print_except()
        try:
            props["minfreq"], props["maxfreq"] = props["frange"]
        except:
            print_except()
        for d in data:
            d_str = " ".join([str(p) for p in d])
            self._logger.write(self._format.format(data=d_str, **props))
    def _res_cb(self, iface, name, res, props, args, kwargs):
        if name == "radio":
            self._write_radio(res["data"], cmd_name="radio", **res["props"])
        elif name == "npoint":
            for r in res:
                self._logger.write_comment("%f, %f" % tuple(r[0]))
                self._write_radio(r[1]["data"], cmd_name="npoint",
                                  **r[1]["props"])
    def _log_cb(self, iface, name, content):
        string = "%s: %s" % (repr(name), repr(content))
        self._logger.write_comment(string)

setiface.logger.zwicky = ZwickyLogger

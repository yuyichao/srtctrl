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

import time as _time
from srt_comm import *

class ZwickyTracker:
    def __init__(self, zwicky):
        self._zwicky = zwicky
        self.reset()
    def reset(self):
        self._az = 0
        self._el = 0
        self.track()
    def set_pos(self, az, el):
        self._az = float(az)
        self._el = float(el)
    def update_pos(self):
        self._zwicky.move(self._az, self._el)
    def track(self, name="", offset=[0, 0], time=0, abstime=False, track=False,
              args=None, **kw):
        if self._track(name, offset, time, abstime, track, args):
            self._zwicky.send_signal("track", self._track_obj)
            return True
        return False
    def _track(self, name, offset, time, abstime, track, args):
        if track:
            if abstime:
                try:
                    time = guess_time(time) - _time.time()
                except:
                    time = 0
            else:
                try:
                    time = guess_interval(time)
                except:
                    time = 0
        else:
            if abstime:
                try:
                    time = guess_time(time)
                except:
                    time = _time.time()
            else:
                try:
                    time = guess_interval(time) + _time.time()
                except:
                    time = _time.time()
        self._track_obj = {"name": name, "offset": offset, "time": time,
                           "track": track, "args": args}
        self._zwicky.send_track(name, offset, time, track, args)
        return True
    def get_track(self):
        return self._track_obj

iface.zwicky.tracker = ZwickyTracker

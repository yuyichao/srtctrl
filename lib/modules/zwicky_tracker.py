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
import time as _time
from srt_comm import *

class ZwickyTracker:
    def __init__(self, zwicky):
        self._zwicky = zwicky
        self._waiting = 0
        self._track_obj = None
        self._station_changed = False
        self._zwicky.get_config("station")
        self._zwicky.connect("alarm::track", self._track_cb)
        self._zwicky.connect("config", self._config_cb)
        self.reset()
    def _config_cb(self, zwicky, field, name, value):
        if field == "zwicky" and name == "station":
            self._station_changed = True
            self._check_station()
            return
    def _check_station(self):
        if not self._station_changed:
            return
        if self._waiting:
            return
        self._station_changed = False
        if self._track_obj is None:
            return
        track_obj = self.get_track()
        self._apply_track(track_obj)
    def _track_cb(self, zwicky, name, nid, args):
        try:
            az, el = args["az"], args["el"]
        except:
            return
        try:
            if not args["track"] == self._track_obj:
                self._track_obj = args["track"]
                self._zwicky.send_signal("track", self._track_obj)
        except:
            pass
        try:
            self.set_pos(az, el)
        except:
            return
        self._update_pos()
    def reset(self):
        self._az = -10
        self._el = -10
        self.track(args=[-10, -10], track=False)
    def set_pos(self, az, el):
        self._az = float(az)
        self._el = float(el)
    def _update_pos(self):
        self._zwicky.move(self._az, self._el)
    def track(self, name="", offset=[0, 0], time=0, track=True,
              args=None, **kw):
        return self._track(name, offset, time, track, args)
    def _apply_track(self, track_obj):
        track_obj["station"] = self._zwicky.configs.station
        self._waiting += 1
        res = self._zwicky.send_chk_alarm("track", "zwicky", track_obj)
        if res is None:
            self._waiting -= 1
            self._check_station()
            return
        res = self._zwicky.wait_with_cb(
            lambda pkg: (pkg["type"] == "alarm" and
                         pkg["name"] == "track" and
                         pkg["nid"] == "zwicky"), check_only=True)
        self._waiting -= 1
        self._check_station()
        return True
    def _track(self, name, offset, time, track, args):
        # offset = std_arg([0., 0.], offset)
        # time = try_get_interval(time)
        # if time is None:
        #     time = 0
        # if not track:
        #     time += _time.time()
        track_obj = {"name": name, "offset": offset, "time": time,
                     "track": track, "args": args}
        return self._apply_track(track_obj)
    def get_track(self):
        return self._track_obj.copy()
    def set_offset(self, off_x, off_y):
        if self._waiting:
            raise Exception
        track_obj = self.get_track()
        track_obj["offset"] = [off_x, off_y]
        self._apply_track(track_obj)
    def get_offset(self):
        return self.get_track()["offset"]
    def add_offset(self, add_x, add_y):
        off_x, off_y = self.get_offset()
        self.set_offset(off_x + add_x, off_y + add_y)

setiface.device.zwicky.tracker = ZwickyTracker

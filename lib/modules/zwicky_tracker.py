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
        self._track_obj = None
        self._zwicky.get_config("station")
        self._zwicky.connect("alarm::track", self._track_cb)
        self._zwicky.connect("config", self._config_cb)
        self.reset()
    def _config_cb(self, zwicky, field, name, value):
        if field == "zwicky" and name == "station":
            if self._track_obj is None:
                return
            track_obj = self.get_track()
            self._apply_track(track_obj)
            return
    def _track_cb(self, zwicky, name, nid, args):
        az, el = get_dict_fields(args, ["az", "el"])
        if None in [az, el]:
            return
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
        if self._track(name, offset, time, track, args):
            self._zwicky.send_signal("track", self._track_obj)
            return True
        return False
    def _apply_track(self, track_obj):
        track_obj["station"] = self._zwicky.configs.station
        res = self._zwicky.send_chk_alarm("track", "zwicky", track_obj)
        if res is None:
            return
        self._track_obj = track_obj
        res = self._zwicky.wait_with_cb(
            lambda pkg: (pkg["type"] == "alarm" and
                         pkg["name"] == "track" and
                         pkg["nid"] == "zwicky"), check_only=True)
        return True
    def _track(self, name, offset, time, track, args):
        offset = std_arg([0., 0.], offset)
        time = try_get_interval(time)
        if t is None:
            time = 0
        if not track:
            time += _time.time()
        track_obj = {"name": name, "offset": offset, "time": time,
                     "track": track, "args": args}
        return self._apply_track(track_obj)
    def get_track(self):
        return self._track_obj.copy()

setiface.device.zwicky.tracker = ZwickyTracker

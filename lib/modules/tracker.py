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
from srt_comm.parsetime import *
from srt_comm import *
from gi.repository import GObject, GLib
import time as _time

class SrtTracker(GObject.Object):
    __gsignals__ = {
        "alarm": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_PYOBJECT,)),
    }
    def __init__(self, name='', offset=[0, 0], time=0, track=True,
                 args=None, station=[0, 0, 0], **kwargs):
        super(SrtTracker, self).__init__()
        if not name:
            name = "simple"
        self._args = args
        self._plugin = getiface.alarm.trackers[name](args)
        self._name = name
        try:
            self._off_az, self._off_el = [guess_angle(agl)
                                          for agl in offset[:2]]
        except:
            self._off_az, self._off_el = [0, 0]
        self._track = bool(track)
        if self._track:
            try:
                self._time = guess_interval(time)
            except:
                self._time = 0
        else:
            try:
                self._time = guess_time(time)
            except:
                self._time = _time.time()

        self._station_az, self._station_el = [guess_angle(agl)
                                              for agl in station[:2]]
        try:
            self._station_hi = float(station[2])
        except:
            self._station_hi = 0
        if self._track:
            GLib.timeout_add_seconds(1, self._timeout_cb)
        GLib.idle_add(self._idle_cb)
        self._active = True
    def _get_track_obj(self):
        return {"name": self._name, "offset": [self._off_az, self._off_el],
                "time": self._time, "track": self._track, "args": self._args,
                "station": [self._station_az, self._station_el,
                            self._station_hi]}
    def _timeout_cb(self):
        return self._update_cb()
    def _idle_cb(self):
        self._update_cb()
        return False
    def _update_cb(self):
        if not self._active:
            return False
        if self._track:
            time = _time.time() + self._time
        else:
            time = self._time
        station = [self._station_az, self._station_el, self._station_hi]
        _az, _el = self._plugin(station, time)
        az, el = ae_with_offset_as([_az, _el], [self._off_az, self._off_el],
                                   base_type='xy',  offset_type='xy',
                                   comp_type='xy')
        if -180 < self._off_az < 180:
            az = (az - _az + 180) % 360 + _az - 180
        elif self._off_az >= 0:
            az = (az - _az) % 360 + _az
        else:
            az = (az - _az) % 360 + _az - 360
        self.emit("alarm", {"az": az, "el": el,
                            "track": self._get_track_obj()})
        return self._track
    def stop(self):
        self._active = False

setiface.alarm.track = SrtTracker

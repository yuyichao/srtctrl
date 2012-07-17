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
        self._plugin = getiface.alarm.trackers[name](args)
        self._name = name
        try:
            self._off_az, self._off_el = offset
            self._off_az, self._off_el = float(self._off_az), float(self._off_el)
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

        self._station_az, self._station_el = station[:2]
        self._station_az, self._station_el = (float(self._station_az),
                                              float(self._station_el))
        try:
            self._station_hi = float(station[2])
        except:
            self._station_hi = 0
        if self._track:
            GLib.timeout_add_seconds(1, self._update_cb)
        else:
            GLib.idle_add(self._update_cb)
        self._active = True
    def _update_cb(self):
        if not self._active:
            return False
        if self._track:
            time = _time.time() + self._time
        else:
            time = self._time
        station = [self._station_az, self._station_el, self._station_hi]
        az, el = self._plugin(station, time)
        # TODO better offset
        az += self._off_az
        el += self._off_el
        self.emit("alarm", {"az": az, "el": el})
        return self._track
    def stop(self):
        self._active = False

setiface.alarm.track = SrtTracker

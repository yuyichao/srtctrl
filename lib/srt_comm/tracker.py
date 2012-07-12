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

from .module import SrtPlugins
from gi.repository import GObject, GLib
import time as _time

class SrtTracker(GObject.Object):
    __gsignals__ = {
        "update": (GObject.SignalFlags.RUN_FIRST,
                   GObject.TYPE_NONE,
                   (GObject.TYPE_DOUBLE, GObject.TYPE_DOUBLE)),
    }
    def __init__(self, name='', offset=[0, 0], time=0,
                 abstime=False, track=False, args=None, **kwargs):
        super().__init__()
        if not name:
            name = "simple"
        self._plugin = SrtPlugins().tracker[name](args)
        self._name = name
        self._off_az, self._off_el = offset
        if abstime:
            self._offtime = time - _time.time()
        else:
            self._offtime = float(time)
        self._track = bool(track)
        if self._track:
            GLib.timeout_add_seconds(1, self._update_cb)
        else:
            GLib.idle_add(self._update_cb)
        self._active = True
    def _update_cb(self):
        if not self._active:
            return False
        time = _time.time() + self._offtime
        az, el = self._plugin(time)
        # TODO add offset
        self.emit("update", az, el)
        return self._track
    def stop(self):
        self._active = False

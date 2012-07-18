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
from gi.repository import GObject, GLib

class SrtTimer(GObject.Object):
    __gsignals__ = {
        "alarm": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_PYOBJECT,)),
    }
    def __init__(self, timeout=1000, **kwargs):
        super(SrtTimer, self).__init__()
        timeout = int(timeout)
        GLib.timeout_add(timeout, self._update_cb)
        self._active = True
    def _update_cb(self):
        if not self._active:
            return False
        self.emit("alarm", True)
        return True
    def stop(self):
        self._active = False

setiface.alarm.timer = SrtTimer

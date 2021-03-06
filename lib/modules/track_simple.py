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
class TrackSimple:
    def __init__(self, args):
        try:
            self._az, self._el = [float(i) for i in args]
        except:
            self._az, self._el = [0, 0]
    def __call__(self, station, time):
        return self._az, self._el

setiface.alarm.trackers.simple = TrackSimple
setiface.alarm.trackers.Simple = TrackSimple
setiface.alarm.trackers.azel = TrackSimple
setiface.alarm.trackers.AzEl = TrackSimple

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
import ephem, datetime
from math import *

def rad2deg(agls):
    if isnum(agls):
        return agls * 180 / pi
    return [rad2deg(agl) for agl in agls]

def deg2rad(agls):
    if isnum(agls):
        return agls * pi / 180
    return [deg2rad(agl) for agl in agls]

def mk_observer(station, time):
    o = ephem.Observer()
    o.date = datetime.datetime.utcfromtimestamp(time)
    o.pressure = 0
    o.lon, o.lat = deg2rad(station[:2])
    o.elev = station[2]
    return o

setiface.utils.ephem.mk_observer = mk_observer
setiface.utils.ephem.rad2deg = rad2deg
setiface.utils.ephem.deg2rad = deg2rad

class TrackSun:
    def __init__(self, args):
        self._sun = ephem.Sun()
    def __call__(self, station, time):
        o = mk_observer(station, time)
        self._sun.compute(o)
        return rad2deg([self._sun.az, self._sun.alt])

setiface.alarm.trackers.sun = TrackSun

class TrackGalactic:
    def __init__(self, args):
        try:
            self._az, self._el = [float(i) for i in args]
        except:
            self._az, self._el = [0, 0]
        gal = ephem.Galactic(*deg2rad([self._az, self._el]),
                             epoch=ephem.J2000)
        self._p = ephem.FixedBody()
        self._p._ra, self._p._dec = [float(i) for i in gal.to_radec()]
    def __call__(self, station, time):
        o = mk_observer(station, time)
        self._p.compute(o)
        return rad2deg([self._p.az, self._p.alt])

setiface.alarm.trackers.galactic = TrackGalactic

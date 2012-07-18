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

def zwicky_pos(zwicky):
    return [zwicky.motor.az, zwicky.motor.el]

setiface.props.zwicky.pos = zwicky_pos

def zwicky_track(zwicky):
    return zwicky.tracker.get_track()

setiface.props.zwicky.track = zwicky_track

def zwicky_freq_mode(zwicky):
    return zwicky.radio.get_freq()

setiface.props.zwicky.freq_mode = zwicky_freq_mode

def zwicky_calib(zwicky):
    return zwicky.radio.get_calib()

setiface.props.zwicky.calib = zwicky_calib

def zwicky_sys_tmp(zwicky):
    return zwicky.radio.get_sys_tmp()

setiface.props.zwicky.sys_tmp = zwicky_sys_tmp

def zwicky_offset(zwicky):
    return zwicky.motor.get_offset()

setiface.props.zwicky.offset = zwicky_offset

def zwicky_gala_pos(zwicky):
    import ephem
    o = getiface.utils.ephem.mk_observer(zwicky.configs.station,
                                         zwicky_time(zwicky))
    pos = getiface.utils.ephem.deg2rad(zwicky_pos(zwicky))
    radec = o.radec_of(*pos)
    p = ephem.FixedBody()
    p._ra, p._dec = radec
    p.compute(o)
    ga = ephem.Galactic(p, epoch=ephem.J2000)
    return getiface.utils.ephem.rad2deg([ga.lon, ga.lat])

setiface.props.zwicky.gala_pos = zwicky_gala_pos

def zwicky_time(zwicky):
    return _time.time()

setiface.props.zwicky.time = zwicky_time

def zwicky_source_on(zwicky):
    return zwicky.source_on

setiface.props.zwicky.source_on = zwicky_source_on

def zwicky_frange(zwicky):
    return zwicky.radio.get_frange()

setiface.props.zwicky.frange = zwicky_frange

def zwicky_station(zwicky):
    return zwicky.configs.station

setiface.props.zwicky.station = zwicky_station

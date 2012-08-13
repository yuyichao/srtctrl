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
import time as _time

def zwicky_move(zwicky, name="", args=None, offset=[0., 0.], time=0,
                track=True, *w, **kw):
    name = std_arg("", name)
    offset = std_arg([0., 0.], offset)
    track = std_arg(False, track)
    if not zwicky.track(name=name, offset=offset, time=time,
                        track=track, args=args):
        raise Exception
    zwicky.motor.pos_chk()
    return True

setiface.cmds.zwicky.move = zwicky_move

def zwicky_galactic(zwicky, gaz=0, gel=0, *w, **kw):
    return zwicky_move(zwicky, "galactic", args=[gaz, gel])

setiface.cmds.zwicky.galactic = zwicky_galactic
setiface.cmds.zwicky.gala = zwicky_galactic
setiface.cmds.zwicky.Galactic = zwicky_galactic
setiface.cmds.zwicky.Gala = zwicky_galactic

setiface.cmds.zwicky.sun = lambda zwicky, *w, **kw: zwicky_move(zwicky, "sun")
setiface.cmds.zwicky.Sun = lambda zwicky, *w, **kw: zwicky_move(zwicky, "sun")

def zwicky_azel(zwicky, az=0, el=0, *w, **kw):
    return zwicky_move(zwicky, "simple", args=[az, el])

setiface.cmds.zwicky.azel = zwicky_azel
setiface.cmds.zwicky.AzEl = zwicky_azel

def _get_galactic(d):
    return lambda zwicky, *w, **kw: zwicky_galactic(zwicky, d, 0)

for d in range(0, 180, 5):
    setiface.cmds.zwicky["G%d" % d] = _get_galactic(d)
    setiface.cmds.zwicky["g%d" % d] = _get_galactic(d)

def zwicky_calib(zwicky, count=1, *w, **kw):
    res = zwicky.calib(int(count))
    return res

setiface.cmds.zwicky.calib = zwicky_calib
setiface.cmds.zwicky.noisecal = zwicky_calib
setiface.cmds.zwicky.calibrate = zwicky_calib
setiface.cmds.zwicky.Calib = zwicky_calib
setiface.cmds.zwicky.NoiseCal = zwicky_calib
setiface.cmds.zwicky.Calibrate = zwicky_calib

def zwicky_reset(zwicky, *w, **kw):
    zwicky.reset()
    return True

setiface.cmds.zwicky.reset = zwicky_reset
setiface.cmds.zwicky.stow = zwicky_reset

def zwicky_radio(zwicky, count=1, interval=None, until=None, *w, **kw):
    count = int(count)
    time_limit = None
    try:
        int_limit = guess_interval(interval) + _time.time()
        if time_limit is None or time_limit > int_limit:
            time_limit = int_limit
    except:
        pass
    try:
        until_limit = guess_time(until)
        if time_limit is None or time_limit > until_limit:
            time_limit = until_limit
    except:
        pass
    if count <= 0:
        count = 1
    f_res = []
    f_frange = None
    for i in range(count):
        zwicky.motor.pos_chk()
        res1 = zwicky.radio.radio()
        f_frange = res1["freq_range"]
        f_res.append(res1["data"])
        # so we will always take at least one set of data here
        # why would anyone ever want to take no data?...
        if not time_limit is None and time_limit < _time.time():
            break
    return {"data": f_res, "frange": f_frange, "props": zwicky.get_all_props()}

setiface.cmds.zwicky.radio = zwicky_radio

def zwicky_set_freq(zwicky, freq=None, mode=None, *w, **kw):
    freq = None if freq is None else float(freq)
    mode = None if mode is None else int(mode)
    if not mode > 0:
        raise TypeError
    zwicky.radio.set_freq(freq, mode)

setiface.cmds.zwicky.set_freq = zwicky_set_freq
setiface.cmds.zwicky.freq = zwicky_set_freq

def zwicky_set_offset(zwicky, az=0., el=0., *w, **kw):
    az = float(az)
    el = float(el)
    zwicky.set_config("poffset", [az, el])
    zwicky.motor.pos_chk()

setiface.cmds.zwicky.set_offset = zwicky_set_offset
setiface.cmds.zwicky.offset = zwicky_set_offset

def zwicky_npoint(zwicky, x_half=1, y_half=1, x_step=2, y_step=2,
                  count=1, interval=None, y_first=True, *w, **kw):
    x_half = int(x_half)
    y_half = int(y_half)
    x_step = float(x_step)
    y_step = float(y_step)
    count = int(count)
    if x_half < 0 or y_half < 0 or x_step < 0 or y_step < 0:
        raise Exception
    track_obj = zwicky.tracker.get_track()
    if not track_obj["track"]:
        abstime = track_obj["time"]
    x_base, y_base = track_obj["offset"]
    if y_first:
        offsets = ((x * x_step, y * y_step)
                   for x in range(-x_half, x_half + 1)
                   for y in range(-y_half, y_half + 1))
    else:
        offsets = ((x * x_step, y * y_step)
                   for y in range(-y_half, y_half + 1)
                   for x in range(-x_half, x_half + 1))
    results = []
    for x_off, y_off in offsets:
        track_obj["offset"] = [x_base + x_off, y_base + y_off]
        if not track_obj["track"]:
            track_obj["time"] - _time.time()
        if not zwicky.track(**track_obj):
            raise Exception
        zwicky.motor.pos_chk()
        res = zwicky_radio(zwicky, count=count, interval=interval)
        results.append([(x_off, y_off), res])
    track_obj["offset"] = [x_base, y_base]
    if not zwicky.track(**track_obj):
        raise Exception
    zwicky.motor.pos_chk()
    zwicky.send_signal("npoint", results)
    return results;

setiface.cmds.zwicky.npoint = zwicky_npoint

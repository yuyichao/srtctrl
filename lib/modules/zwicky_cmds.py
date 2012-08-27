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

def zwicky_radec(zwicky, ra=0, dec=0, *w, **kw):
    return zwicky_move(zwicky, "radec", args=[ra, dec])

setiface.cmds.zwicky.radec = zwicky_radec
setiface.cmds.zwicky.RaDec = zwicky_radec

def _get_galactic(d):
    return lambda zwicky, *w, **kw: zwicky_galactic(zwicky, d, 0)

for d in range(0, 180, 5):
    setiface.cmds.zwicky["G%d" % d] = _get_galactic(d)
    setiface.cmds.zwicky["g%d" % d] = _get_galactic(d)

def zwicky_calib(zwicky, count=1, *w, **kw):
    res = zwicky.calib(int(round(float(count))))
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

def zwicky_quit(zwicky, *w, **kw):
    zwicky.reset()
    zwicky.send_quit()
    return True

setiface.cmds.zwicky.quit = zwicky_quit
setiface.cmds.zwicky.exit = zwicky_quit

def zwicky_radio(zwicky, count=1, interval=None, until=None, *w, **kw):
    count = int(round(float(count)))
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
    i = 0
    while True:
        zwicky.motor.pos_chk()
        res1 = zwicky.radio.radio()
        f_frange = res1["freq_range"]
        f_res.append(res1["data"])
        # so we will always take at least one set of data here
        # why would anyone ever want to take no data?...
        i += 1
        if i < count:
            continue
        if time_limit is None or time_limit < _time.time():
            break
    return {"data": f_res, "frange": f_frange, "props": zwicky.get_all_props()}

setiface.cmds.zwicky.radio = zwicky_radio

def zwicky_set_freq(zwicky, freq=None, mode=None, *w, **kw):
    freq = None if freq is None else float(freq)
    mode = None if mode is None else int(round(float(mode)))
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

def zwicky_npoint(zwicky, x_count=3, y_count=3, x_step=2, y_step=2,
                  count=1, interval=None, angle=0, *w, **kw):
    x_count = int(round(float(x_count)))
    y_count = int(round(float(y_count)))
    x_step = float(x_step)
    y_step = float(y_step)
    angle = float(angle)
    count = int(round(float(count)))
    if x_count <= 0 or y_count < 0 or x_step < 0 or y_step < 0:
        raise Exception
    offsets = (rot_2d((x - (x_count - 1) / 2.) * x_step,
                      (y - (y_count - 1) / 2.) * y_step, angle)
               for y in range(y_count)
               for x in range(x_count))
    results = []
    base_x, base_y = zwicky.tracker.get_offset()
    for x_off, y_off in offsets:
        zwicky.tracker.set_offset(x_off + base_x, y_off + base_y)
        res = zwicky_radio(zwicky, count=count, interval=interval)
        results.append([(x_off, y_off), res])
    zwicky.tracker.set_offset(base_x, base_y)
    zwicky.motor.pos_chk()
    zwicky.send_signal("npoint", results)
    return results;

setiface.cmds.zwicky.npoint = zwicky_npoint

def zwicky_set_track_offset(zwicky, az=0, el=0, *w, **kw):
    az = float(az)
    el = float(el)
    zwicky.tracker.set_offset(az, el)
    zwicky.motor.pos_chk()

setiface.cmds.zwicky.set_track_offset = zwicky_set_track_offset
setiface.cmds.zwicky.track_offset = zwicky_set_track_offset

def zwicky_add_track_offset(zwicky, az=0, el=0, *w, **kw):
    az = float(az)
    el = float(el)
    zwicky.tracker.add_offset(az, el)
    zwicky.motor.pos_chk()

setiface.cmds.zwicky.add_track_offset = zwicky_add_track_offset
setiface.cmds.zwicky.add_offset = zwicky_add_track_offset

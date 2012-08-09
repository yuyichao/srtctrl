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

def zwicky_move(zwicky, name="", args=None, offset=[0., 0.], time=0,
                abstime=False, track=True, *w, **kw):
    name = std_arg("", name)
    offset = std_arg([0., 0.], offset)
    abstime = std_arg(False, abstime)
    track = std_arg(False, track)
    if not zwicky.track(name=name, offset=offset, time=time,
                        abstime=abstime, track=track, args=args):
        raise Exception
    zwicky.motor.pos_chk()
    return True

setiface.cmds.zwicky.move = zwicky_move

def zwicky_calib(zwicky, count=1, *w, **kw):
    res = zwicky.calib(count)
    return res

setiface.cmds.zwicky.calib = zwicky_calib
setiface.cmds.zwicky.noicecal = zwicky_calib

def zwicky_reset(zwicky, *w, **kw):
    zwicky.reset()
    return True

setiface.cmds.zwicky.reset = zwicky_reset
setiface.cmds.zwicky.stow = zwicky_reset

def zwicky_radio(zwicky, count=1, *w, **kw):
    count = int(count)
    if count <= 0:
        count = 1
    f_res = []
    f_frange = None
    for i in range(count):
        zwicky.motor.pos_chk()
        res1 = zwicky.radio.radio()
        f_frange = res1["freq_range"]
        f_res.append(res1["data"])
    return {"data": f_res, "frange": f_frange}

setiface.cmds.zwicky.radio = zwicky_radio

def zwicky_set_freq(zwicky, freq=None, mode=1, *w, **kw):
    freq = float(freq)
    mode = int(mode)
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

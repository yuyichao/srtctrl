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

def zwicky_move(zwicky, name="", offset=[0., 0.], time=0, abstime=False,
                track=True, args=None, *w, **kw):
    name = std_arg("", name)
    offset = std_arg([0., 0.], offset)
    abstime = std_arg(False, abstime)
    track = std_arg(False, track)
    if not zwicky.track(name=name, offset=offset, time=time,
                        abstime=abstime, track=track, args=args):
        return
    return {"type": "move", "res": True}

setiface.cms.zwicky.move = zwicky_move

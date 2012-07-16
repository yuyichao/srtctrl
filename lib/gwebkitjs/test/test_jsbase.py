#!/usr/bin/env python

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
from gi.repository import GWebKitJS

def printr():
    _print = print
    def printr(*arg, **kwarg):
        end = '\n'
        if 'end' in kwarg:
            end = kwarg['end']
        kwarg['end'] = ''
        _print('\033[31;1m', end='')
        _print(*arg, **kwarg)
        _print('\033[0m', end=end)
    return printr
printr = printr()

def _print():
    _print = print
    def __print(*arg, **kwarg):
        end = '\n'
        if 'end' in kwarg:
            end = kwarg['end']
        kwarg['end'] = ''
        _print('\033[32;1m', end='')
        _print(*arg, **kwarg)
        _print('\033[0m', end=end)
    return __print
print = _print()

printr('\nTest Start')

ctx = GWebKitJS.Context.new(None)
print(ctx)

class MObj(GWebKitJS.Base):
    def __init__(self):
        print("__init__")
    def do_has_property(self, ctx, name):
        if name == 'a':
            return True
        return False
    def do_get_property(self, ctx, name):
        if name == 'a':
            return ctx.make_number(1)
    def do_get_property_names(self, ctx):
        print("get_property_names")
        return GWebKitJS.util_list_to_obj(['a'])

GWebKitJS.Base.set_name(MObj, "PY")
GWebKitJS.Base.set_name(MObj, "MObj")
GWebKitJS.Base.set_name(MObj, "RegExp")

mobj = ctx.make_object(MObj)
GWebKitJS.Base.set_name(MObj, "A")
mobj = ctx.make_object(MObj)
print(ctx.get_name_str(mobj))
print(ctx.get_property_names(mobj))
print(ctx.to_number(ctx.get_property(mobj, "a")))

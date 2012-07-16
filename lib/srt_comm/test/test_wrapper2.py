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
from srt_comm import *

def new_dict_wrapper():
    d = {}
    def getter(key1, key2):
        return d[key1][key2]
    def setter(key1, key2, value):
        if not key1 in d:
            d[key1] = {}
        d[key1][key2] = value
    def p():
        print(d)
    return p, new_wrapper2(getter, setter)

p, obj = new_dict_wrapper()
p2, obj2 = new_dict_wrapper()

p()
p2()
obj.a.b = 1
obj.c.e = 3
obj.a.j = "asdf"
obj.c.ll = [1, 2]
obj.k.a = None
obj.lll.s = "m"
obj.lll.s = 1234

obj2.a.b = 188
obj2.c.d = 3412
obj2.a.j = "aslllllllll"
obj2.c.ll = [1, 2, 4]
obj2.k.a = {}
obj2.lll.s = "mkkk"
p()
p2()
print(obj.lll.s)

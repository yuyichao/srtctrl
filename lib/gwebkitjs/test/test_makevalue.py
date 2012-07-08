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
ctx = GWebKitJS.Context.new(None)
print(ctx)
globalobj = ctx.get_global()
print(globalobj)
print(ctx.to_string(globalobj))
print(ctx.to_json_str_simple(globalobj))
print(ctx.to_json_str(globalobj, 2))

for make in [(ctx.make_bool, True),
             (ctx.make_bool, False),
             (ctx.make_null,),
             (ctx.make_undefined,),
             (ctx.make_number, 1.2345),
             (ctx.make_string, 'random string'),
             (ctx.make_from_json_str, ('{"a": "b", "c": 1234,'
                                       ' "ddd": [1, 2, "3",'
                                       ' true, null, false, {"1": 22}]}')),
             (ctx.make_from_json_str, ('[1, 2, null, false, "ddd2", {}]')),
             ]:
    obj = make[0](*make[1:])
    print()
    print(obj)
    print(ctx.get_name_str(obj))
    print(ctx.to_string(obj))
    print(ctx.to_json_str(obj, 2))

print(ctx.get_name_str(None))

printr('Test End\n')

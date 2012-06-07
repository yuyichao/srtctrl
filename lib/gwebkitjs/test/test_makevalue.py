#!/usr/bin/env python

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

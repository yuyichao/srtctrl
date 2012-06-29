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

mobj = GWebKitJS.Base.new(ctx, MObj)
print(ctx.get_name_str(mobj))
print(ctx.get_property_names(mobj))
print(ctx.to_number(ctx.get_property(mobj, "a")))

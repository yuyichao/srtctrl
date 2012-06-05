#!/usr/bin/env python

from gi.repository import GWebKitJS

print('\n\nTest Start\n')

ctx = GWebKitJS.Context.new(None)
vs = []
vs.append(ctx.make_bool(True))
vs.append(ctx.make_from_json_str('["ab", "cd", {"aa": "bb", "cc": 1}]'))
vs.append(ctx.make_from_json_str('undefined'))
vs.append(ctx.make_null())
vs.append(ctx.make_undefined())
vs.append(ctx.make_string("alkd;lkfa;jsdlkfj;alskd;jfalkds"))
vs.append(ctx.make_number(1.11231373984))

for v in vs:
    print(ctx.to_json_str(v, 0))
    print(ctx.get_value_type(v))
    print()

print('\nTest Ended\n\n')

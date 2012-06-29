from gi.repository import (GWebKitJS as _gwkjs), (GLib as _GLib)

def _js2array(ctx, jsobj):
    try:
        n = ctx.get_property("length")
    except _GLib.GError:
        return []
    res = [None] * n
    for i in range(n):
        try:
            jsele = ctx.get_property_at_index(jsobj, i)
            res[i] = js2py(ctx, jsele)
        except _GLib.GError:
            pass
    return res

def js2py(ctx, jsobj):
    jstype = ctx.get_value_type(jsobj)
    if jstype in [_gwkjs.ValueType.UNKNOWN,
                  _gwkjs.ValueType.UNDEFINED,
                  _gwkjs.ValueType.NULL]:
        return None
    elif jstype == _gwkjs.ValueType.BOOLEAN:
        return ctx.to_boolean(jstype)
    elif jstype == _gwkjs.ValueType.NUMBER:
        return ctx.to_number(jstype)
    elif jstype == _gwkjs.ValueType.STRING:
        return ctx.to_string(jstype)
    if jstype != _gwkjs.ValueType.OBJECT:
        return None
    jsname = ctx.get_name_str(jsobj)
    if not jsname:
        return None
    if jsname == "[object Array]":
        return _js2array(ctx, jsobj)
    return jsobj

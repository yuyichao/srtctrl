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
from gi.repository import GWebKitJS as _gwkjs, GLib as _GLib
import sys

from pywkjs.pywrap import WKPYObject
from pywkjs.jswrap import WKJSObject


def isnum(i):
    return isinstance(i, int) or isinstance(i, float)
if sys.version_info[0] >= 3:
    def isstr(s):
        return isinstance(s, str)
else:
    def isstr(s):
        return isinstance(s, str) or isinstance(s, unicode)

def _js2array(ctx, jsobj):
    try:
        n = int(ctx.to_number(ctx.get_property(jsobj, "length")))
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

def _js2dict(ctx, jsobj):
    try:
        names = ctx.get_property_names(jsobj)
    except _GLib.GError:
        return {}
    res = {}
    for name in names:
        try:
            jsele = ctx.get_property(jsobj, name)
            res[name] = js2py(ctx, jsele)
        except _GLib.GError:
            pass
    return res

def js2py(ctx, jsobj, jsthis=None):
    jstype = ctx.get_value_type(jsobj)
    if jstype in [_gwkjs.ValueType.UNKNOWN,
                  _gwkjs.ValueType.UNDEFINED,
                  _gwkjs.ValueType.NULL]:
        return None
    elif jstype == _gwkjs.ValueType.BOOLEAN:
        return ctx.to_bool(jsobj)
    elif jstype == _gwkjs.ValueType.NUMBER:
        num = ctx.to_number(jsobj)
        if round(num) == num:
            num = int(round(num))
        return num
    elif jstype == _gwkjs.ValueType.STRING:
        return ctx.to_string(jsobj)
    if not jstype == _gwkjs.ValueType.OBJECT:
        return None
    if isinstance(jsobj, WKPYObject):
        return jsobj._pyobj
    jsname = ctx.get_name_str(jsobj)
    if not jsname:
        return None
    if jsname == "[object Array]":
        return _js2array(ctx, jsobj)
    if jsname == '[object Object]':
        return _js2dict(ctx, jsobj)
    return WKJSObject(ctx, jsobj, jsthis=jsthis)

if sys.version_info[0] >= 3:
    def isstr(s):
        return isinstance(s, str)
else:
    def isstr(s):
        return isinstance(s, basestring)

def py2js(ctx, pyobj):
    if pyobj is None:
        return ctx.make_null()
    elif isinstance(pyobj, bool):
        return ctx.make_bool(pyobj)
    elif isnum(pyobj):
        return ctx.make_number(float(pyobj))
    elif isstr(pyobj):
        return ctx.make_string(pyobj)
    elif isinstance(pyobj, list) or isinstance(pyobj, tuple):
        ary = list(pyobj)
        jsary = []
        for ele in ary:
            jsary.append(py2js(ctx, ele))
        return ctx.make_array(jsary)
    if isinstance(pyobj, _gwkjs.Value):
        return pyobj
    if isinstance(pyobj, WKJSObject):
        return pyobj._jsvalue
    return WKPYObject.new(ctx, pyobj)

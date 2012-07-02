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

from gi.repository import GWebKitJS as _gwkjs

import pywkjs

import math as _math

def js2py(*args, **kwargs):
    return pywkjs.general.js2py(*args, **kwargs)
def py2js(*args, **kwargs):
    return pywkjs.general.py2js(*args, **kwargs)

def _std_key(key):
    try:
        key = _math.floor(key + .5)
    except TypeError:
        pass
    return str(key)

class WKJSObject(object):
    def __init__(self, jsctx, jsvalue, jsthis=None):
        super().__setattr__('_jsctx', jsctx)
        super().__setattr__('_jsvalue', jsvalue)
        super().__setattr__('_jsthis', jsthis)
    def __getitem__(self, key):
        key = _std_key(key)
        return js2py(self._jsctx, self._jsctx.get_property(self._jsvalue, key),
                     jsthis=self._jsvalue)
    def __setitem__(self, key, value):
        key = _std_key(key)
        value = py2js(self._jsctx, value)
        self._jsctx.set_property(self._jsvalue, key, value, 0)
    def __delitem__(self, key):
        key = _std_key(key)
        res = self._jsctx.delete_property(self._jsvalue, key)
        if not res:
            raise AttributeError(key)
    def __getattr__(self, key):
        return self.__getitem__(key)
    def __setattr__(self, key, value):
        self.__setitem__(key, value)
    def __delattr__(self, key):
        self.__delitem__(key)
    def __dir__(self):
        return self._jsctx.get_property_names(self._jsvalue)
    def __str__(self):
        return self._jsctx.to_string(self._jsvalue)
    def __repr__(self):
        return self.__str__()
    def __iter__(self):
        return iter(self.__dir__())
    def __call__(self, *args):
        args = [py2js(self._jsctx, arg) for arg in args]
        jsres = self._jsctx.call_function(self._jsvalue, self._jsthis, args)
        return js2py(self._jsctx, jsres)
    def __eq__(self, right):
        right = py2js(self._jsctx, right)
        return self._jsctx.is_equal(self._jsvalue, right)

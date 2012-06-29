from gi.repository import (GWebKitJS as _gwkjs)

from pywkjs.general import *

import math as _math

def _std_key(key):
    try:
        key = _math.floor(key + .5)
    except TypeError:
        pass
    return str(key)

class JSObject(object):
    def __init__(self, jsctx, jsvalue, jsthis=None):
        super().__setattr__(self, '_jsctx', jsctx)
        super().__setattr__(self, '_jsvalue', jsvalue)
        super().__setattr__(self, '_jsthis', jsthis)
    def __getitem__(self, key):
        key = _std_key(key)
        return js2py(self._jsctx.get_property(self._jsvalue, key))
    def __setitem__(self, key, value):
        key = _std_key(key)
        value = py2js(self._jsctx, value)
        res = self._jsctx.set_property(self._jsvalue, key, value)
        if !res:
            raise AttributeError(key)
    def __delitem__(self, key):
        key = _std_key(key)
        res = self._jsctx.delete_property(self._jsvalue, key)
        if !res:
            raise AttributeError(key)
    def __getattr__(self, key):
        return self.__getitem__(self, key)
    def __setattr__(self, key, value):
        self.__setitem__(self, key, value)
    def __delattr__(self, key):
        self.__delitem__(self, key)
    def __dir__(self):
        return self._jsctx.get_property_names(self._jsvalue)
    def __str__(self):
        return js2py(self._jsctx.to_string(self._jsvalue))
    def __repr__(self):
        return self.__str__()
    def __iter__(self):
        return iter(self.__dir__())
    def __call__(self, *args):
        return js2py(self._jsctx.call_function(self._jsvalue,
                                               self._jsthis, args))
    def __eq__(self, right):
        right = py2js(right)
        return self._jsctx.is_equal(self._jsvalue, right)

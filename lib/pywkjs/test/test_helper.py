#!/usr/bin/env python

from pywkjs import *

obj = new_js_global(object())

obj = new_js_global()
obj.a = [1, 2, 3, 4, 5]
print(obj.a)

#!/usr/bin/env python

from pywkjs import *

obj = new_js_global(object())
print(type(obj))
obj.b = {1, 2, 3, 4}
print(obj.b)

obj = new_js_global()
obj.a = [1, 2, 3, 4, 5]
print(obj.a)
string = obj.toString()
print(type(string))
print(string)
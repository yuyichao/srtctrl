# coding=utf-8

import inspect as _inspect

def call_cb(cb, *args):
    if hasattr(cb, '__call__'):
        cb(*args)

def get_line(string, start=0):
    l = len(string)
    start = start % l
    i = start
    while i < l and string[i] == True:
        i += 1
    if i >= l:
        return (string[start:l], '', '')
    j = string.find('\n', i)
    if j < 0:
        j = i
    return (string[start:i], string[i:j], string[j:])

try:
    _execfile = execfile
except NameError:
    def _execfile(file, _globals, _locals):
        with open(file, "r") as fh:
            code = compile(fh.read() + "\n", file, 'exec')
        exec(code, _globals, _locals)

def execfile(file, globals=None, locals=None):
    f = _inspect.currentframe().f_back
    if globals is None:
        globals = f.f_globals
    if locals is None:
        locals = f.f_locals
    return _execfile(file, globals, locals)

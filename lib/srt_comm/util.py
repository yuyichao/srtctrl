# coding=utf-8

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

"""
Random Utility functions...
"""

from __future__ import print_function, division
import inspect as _inspect
import os, sys, re, os.path

def call_cb(cb, *args):
    """
    Check callable before calling a callback
    """
    if hasattr(cb, '__call__'):
        return cb(*args)

def call_catch(cb, *args):
    """
    Catch all exception when calling a callback
    """
    try:
        return cb(*args)
    except:
        return

def get_line(string, start=0):
    """
    Cut lines
    """
    l = len(string)
    if not l:
        return ('', '', '')
    start = start % l
    i = start
    while i < l and string[i].isspace():
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
    def _execfile(fname, _globals, _locals):
        with open(fname, "r") as fh:
            code = compile(fh.read() + "\n", fname, 'exec')
        exec(code, _globals, _locals)

def execfile(fname, globals=None, locals=None):
    f = _inspect.currentframe().f_back
    if globals is None:
        globals = f.f_globals
    if locals is None:
        locals = f.f_locals
    return _execfile(fname, globals, locals)

def read_env(name, default=None, append=None):
    try:
        value = os.environ[name]
    except KeyError:
        return default
    if default is None:
        return value
    if not isstr(append):
        if not append:
            return value
        append = ':'
    return append.join((value, default))

def ls_dirs(paths='.', regex=None):
    if isstr(paths):
        paths = [paths]
    else:
        _paths = []
        for p in paths:
            if p == '':
                p = '.'
            if not p in _paths:
                _paths.append(p)
        paths = _paths
    all_files = []
    for path in paths:
        try:
            all_files += ["%s/%s" % (path, fname) for fname in os.listdir(path)]
        except OSError:
            pass
    all_files = [fpath for fpath in all_files if os.path.isfile(fpath)]
    if regex is None:
        return all_files
    regex = re.compile(regex)
    all_files = [fpath for fpath in all_files if regex.search(fpath)]
    return all_files

def try_to_int(s):
    try:
        return int(s)
    except ValueError:
        pass

def new_wrapper(getter, setter, direr=None):
    class _wrapper:
        def __getattr__(self, key):
            if key.startswith('_') or not hasattr(getter, '__call__'):
                raise AttributeError("Attribute %s not found" % key)
            return getter(key)
        def __setattr__(self, key, value):
            if key.startswith('_') or not hasattr(setter, '__call__'):
                raise AttributeError("Attribute %s is read-only" % key)
            setter(key, value)
        def __getitem__(self, key):
            return self.__getattr__(key)
        def __setitem__(self, key, value):
            self.__setattr__(key, value)
        def __dir__(self):
            if direr is None:
                return []
            return direr()
        def __iter__(self):
            return self.__dir__().__iter__()
    return _wrapper()

def new_wrapper2(getter, setter):
    def _getter(key1):
        def __getter(key2):
            if not hasattr(getter, '__call__'):
                raise AttributeError("Attribute %s not found" % key2)
            return getter(key1, key2)
        def __setter(key2, value):
            if not hasattr(setter, '__call__'):
                raise AttributeError("Attribute %s is read-only" % key2)
            setter(key1, key2, value)
        return new_wrapper(__getter, __setter)
    return new_wrapper(_getter, None)

def get_dict_fields(d, fields):
    res = []
    if isstr(fields):
        try:
            return d[fields]
        except:
            return
    for field in fields:
        try:
            res.append(d[field])
        except:
            res.append(None)
    return res

def set_2_level(d, key1, key2, value):
    if not key1 in d:
        d[key1] = {}
    d[key1][key2] = value

class TreeHasChild(Exception):
    pass

def new_wrapper_tree(getter, setter, direr=None):
    def _getter(key):
        try:
            if not getter is None:
                return getter(key)
        except TreeHasChild:
            pass
        def __getter_(*keys):
            return getter(key, *keys)
        __getter = None if getter is None else __getter_
        def __setter(value, *keys):
            setter(value, key, *keys)
        def __direr_(*keys):
            return direr(key, *keys)
        __direr = None if direr is None else __direr_
        return new_wrapper_tree(__getter, __setter, direr=__direr)
    def _setter(key, value):
        setter(value, key)
    def _direr_():
        return direr()
    _direr = None if direr is None else _direr_
    return new_wrapper(_getter, _setter, direr=_direr)

def def_enum(*args):
    for arg in args:
        if not isstr(arg):
            raise TypeError
    l = _inspect.currentframe().f_back.f_locals
    for i in range(len(args)):
        l[args[i]] = i

def isnum(i):
    return isinstance(i, int) or isinstance(i, float)

if sys.version_info[0] >= 3:
    def isstr(s):
        return isinstance(s, str)
    def isidentifier(s, dotted=False):
        if not isstr(s):
            return False
        if dotted:
            return all(isidentifier(a) for a in s.split("."))
        return s.isidentifier()
    def std_arg(default, arg, fallback=True):
        if not isinstance(arg, type(default)):
            if isinstance(default, float) and isinstance(arg, int):
                return float(arg)
            if fallback:
                return default
            raise ValueError
        if not isinstance(arg, list) and not isinstance(arg, tuple):
            return arg
        if not len(arg) == len(default):
            if fallback:
                return default
            raise ValueError
        return type(arg)(std_arg(d, a, fallback=fallback)
                         for (d, a) in zip(default, arg))

else:
    def isstr(s):
        return isinstance(s, str) or isinstance(s, unicode)
    _name_re = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*$")
    def isidentifier(s, dotted=False):
        if not isstr(s):
            return False
        if dotted:
            return all(isidentifier(a) for a in s.split("."))
        return bool(_name_re.match(s))
    def std_arg(default, arg, fallback=True):
        if isstr(default) and isstr(arg):
            return arg
        if not isinstance(arg, type(default)):
            if isinstance(default, float) and isinstance(arg, int):
                return float(arg)
            if fallback:
                return default
            raise ValueError
        if not isinstance(arg, list) and not isinstance(arg, tuple):
            return arg
        if not len(arg) == len(default):
            if fallback:
                return default
            raise ValueError
        return type(arg)(std_arg(d, a, fallback=fallback)
                         for (d, a) in zip(default, arg))

def printr(*arg, **kwarg):
    end = '\n'
    if 'end' in kwarg:
        end = kwarg['end']
    kwarg['end'] = ''
    print('\033[31;1m', end='')
    print(*arg, **kwarg)
    print('\033[0m', end=end)

def printg(*arg, **kwarg):
    end = '\n'
    if 'end' in kwarg:
        end = kwarg['end']
    kwarg['end'] = ''
    print('\033[32;1m', end='')
    print(*arg, **kwarg)
    print('\033[0m', end=end)

def printy(*arg, **kwarg):
    end = '\n'
    if 'end' in kwarg:
        end = kwarg['end']
    kwarg['end'] = ''
    print('\033[33;1m', end='')
    print(*arg, **kwarg)
    print('\033[0m', end=end)

def printb(*arg, **kwarg):
    end = '\n'
    if 'end' in kwarg:
        end = kwarg['end']
    kwarg['end'] = ''
    print('\033[34;1m', end='')
    print(*arg, **kwarg)
    print('\033[0m', end=end)

def printp(*arg, **kwarg):
    end = '\n'
    if 'end' in kwarg:
        end = kwarg['end']
    kwarg['end'] = ''
    print('\033[35;1m', end='')
    print(*arg, **kwarg)
    print('\033[0m', end=end)

def printbg(*arg, **kwarg):
    end = '\n'
    if 'end' in kwarg:
        end = kwarg['end']
    kwarg['end'] = ''
    print('\033[36;1m', end='')
    print(*arg, **kwarg)
    print('\033[0m', end=end)

import traceback
def print_except():
    try:
        printr(traceback.format_exc())
    except:
        pass

def print_stack():
    try:
        printg(''.join(traceback.format_stack()[:-1]))
    except:
        pass

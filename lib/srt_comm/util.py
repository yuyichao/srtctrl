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

import inspect as _inspect
import os, sys, re, os.path

def call_cb(cb, *args):
    if hasattr(cb, '__call__'):
        cb(*args)

def call_catch(cb, *args):
    try:
        call_cb(cb, *args)
    except:
        return

def get_line(string, start=0):
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

def read_env(name, default=None, append=None):
    try:
        value = os.environ[name]
    except KeyError:
        return default
    if default is None:
        return value
    if not isinstance(append, str):
        if not append:
            return value
        append = ':'
    return append.join((value, default))

def ls_dirs(paths='.', regex=None):
    if isinstance(paths, str):
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

def new_wrapper(getter, setter):
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
    if isinstance(fields, str):
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
    d[key1] = value

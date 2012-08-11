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

from __future__ import print_function, division
import sys
from srt_comm import *
from os import path
import time as _time

def try_get_time(line):
    try:
        tstr, rest = line.split(None, 1)
    except:
        tstr = line
        rest = ''
    try:
        t = guess_interval(tstr)
        t = None if t <= 0 else t
        return t, rest
    except:
        pass
    try:
        t = guess_time(tstr) - _time.time()
        t = None if t <= 0 else t
        return t, rest
    except:
        pass
    return None, line

def try_get_cmd(rest):
    try:
        cmd, arg = rest.split(None, 1)
        return cmd, arg
    except:
        return rest, ''

def sep_line(line):
    t, rest = try_get_time(line)
    cmd, arg = try_get_cmd(rest)
    return t, cmd, arg

def _py_to_str_end(string, start=0, endc='"'):
    l = len(string)
    _pass = False
    for i in range(start, l):
        if _pass:
            _pass = False
            continue
        c = string[i]
        if c == endc:
            return i + 1
        elif c == '\\':
            _pass = True
    return 0

def _py_find_pair(string, start=0):
    l = len(string)
    i = start
    count = {'{}': 0,
             '[]': 0,
             '()': 0}
    found = False
    while i < l:
        c = string[i]
        if c in '"'"'":
            i = _py_to_str_end(string, i + 1, endc=c)
            if i == 0:
                return start
            continue
        elif c == '{':
            count['{}'] += 1
        elif c == '}':
            count['{}'] -= 1
        elif c == '[':
            count['[]'] += 1
        elif c == ']':
            count['[]'] -= 1
        elif c == '(':
            count['()'] += 1
        elif c == ')':
            count['()'] -= 1
        i += 1
        if count['{}'] or count['[]'] or count['()']:
            found = True
            if count['{}'] < 0 or count['[]'] < 0 or count['()'] < 0:
                return i
        else:
            if found:
                return i
    return start

def _py_to_bare_end(string, start=0, extra=""):
    l = len(string)
    if start >= l:
        return start
    for i in range(start, l):
        c = string[i]
        if not (c.isalnum() or isidentifier(c) or c in "-" or c in extra):
            return i
    return i + 1

def get_next_arg(arg):
    arg = arg.strip()
    if not arg:
        return None, None, ''
    if arg[0] == ',':
        return None, None, arg[1:].strip()
    if arg[0] in '"'"'":
        i = _py_to_str_end(arg, start=1, endc=arg[0])
        if i == 0:
            raise SyntaxError("Unclosed quote")
        left = arg[i:].strip()
        if left and left[0] == ',':
            left = left[1:].strip()
        arg = eval(arg[:i], {}, {})
        return None, arg, left
    if arg[0] in "([{":
        i = _py_find_pair(arg, start=0)
        left = arg[i:].strip()
        if left and left[0] == ',':
            left = left[1:].strip()
        arg = eval(arg[:i], {}, {})
        return None, arg, left
    i = _py_to_bare_end(arg, start=1, extra="-./")
    left = arg[i:].strip()
    key = arg[:i]
    if not isidentifier(key):
        try:
            key = float(key)
        except:
            pass
        if left and left[0] == ',':
            left = left[1:].strip()
        return None, key, left
    if left and left[0] == '=':
        left = left[1:].strip()
        if left and left[0] in "([{":
            i = _py_find_pair(left, start=0)
            left1 = left[i:].strip()
            if left1 and left1[0] == ',':
                left1 = left1[1:].strip()
            arg = eval(left[:i], {}, {})
            return key, arg, left1
        elif left and left[0] in '"'"'":
            i = _py_to_str_end(left, start=1, endc=left[0])
            if i == 0:
                raise SyntaxError("Unclosed quote")
            left1 = left[i:].strip()
            if left1 and left1[0] == ',':
                left1 = left1[1:].strip()
            arg = eval(left[:i], {}, {})
            return key, arg, left1
        i = _py_to_bare_end(left, start=1)
        left1 = left[i:].strip()
        if left1 and left1[0] == ',':
            left1 = left[1:].strip()
        arg = eval(left[:i], {}, {})
        return key, arg, left1
    elif left and left[0] == ',':
        left = left[1:].strip()
    return None, key, left

def parse_arg(arg):
    args = []
    kwargs = {}
    arg = arg.strip()
    while arg:
        key, value, arg = get_next_arg(arg)
        if key:
            kwargs[key] = value
        else:
            args.append(value)
        arg = arg.strip()
    return args, kwargs

def get_func(iface, cmd):
    if cmd.lower() == 'record':
        return iface.record
    return iface.cmd[cmd]

def exec_cmd(iface, cmd, arg):
    args, kwargs = parse_arg(arg)
    func = get_func(iface, cmd)
    func(*args, **kwargs)

def exec_line(iface, line):
    if line.startswith('#') or line.startswith('*') or not line:
        return
    t, cmd, arg = sep_line(line)
    if t is None or t <= 0:
        exec_cmd(iface, cmd, arg)
        return
    if not cmd:
        wait_main(t)
        return
    if cmd == 'radio':
        rad_arg = arg
        cmd = ''
        arg = ''
    else:
        rad_arg = ''
    t += _time.time()
    while t >= _time.time():
        exec_cmd(iface, 'radio', rad_arg)
    exec_cmd(iface, cmd, arg)

def main():
    from srt_slave import default
    fname = sys.argv[1]
    fh = open(fname, 'r')
    for line in fh:
        exec_line(default, line.strip(' \n\r\t\b:'))

def start_zwicky_cmd(host, pwd, fname=None, **kw):
    if not isstr(fname):
        return False
    fname = path.abspath(path.join(pwd, fname))
    getiface.slave.python(host, pwd, fname=__file__, args=[fname], **kw)

if __name__ == '__main__':
    main()
elif 'setiface' in globals():
    setiface.slave.zwicky_cmd = start_zwicky_cmd

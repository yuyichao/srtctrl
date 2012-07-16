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
def _j_to_str_end(jstr, start):
    l = len(jstr)
    _pass = False
    for i in range(start, l):
        if _pass:
            _pass = False
            continue
        c = jstr[i]
        if c == '"':
            return i + 1
        elif c == '\\':
            _pass = True
    return 0

def _j_find_start(jstr, start):
    l = len(jstr)
    i = start
    while i < l:
        c = jstr[i]
        if c == '"':
            i = _j_to_str_end(jstr, i + 1)
            if i == 0:
                return l
            continue
        elif c in '{}[]':
            return i
        i += 1
    return l

def _j_find_pair(jstr, start=0):
    l = len(jstr)
    start = _j_find_start(jstr, start)
    i = start
    count = {'{}': 0,
             '[]': 0}
    found = False
    while i < l:
        c = jstr[i]
        if c == '"':
            i = _j_to_str_end(jstr, i + 1)
            if i == 0:
                return (start, start)
            continue
        elif c == '{':
            count['{}'] += 1
        elif c == '}':
            count['{}'] -= 1
        elif c == '[':
            count['[]'] += 1
        elif c == ']':
            count['[]'] -= 1
        i += 1
        if count['{}'] or count['[]']:
            found = True
            if count['{}'] < 0 or count['[]'] < 0:
                return start, i
        else:
            if found:
                return start, i
    return start, start

def get_json(jstr, start=0):
    if not len(jstr):
        return ('', '', '')
    start = start % len(jstr)
    (start1, i) = _j_find_pair(jstr, start=start)
    return (jstr[start:start1], jstr[start1:i], jstr[i:])

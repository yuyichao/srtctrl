#!/usr/bin/env python

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
from srt_comm import get_json

def __test_get_json():
    jstrs = ['     []',
             '     {}',
             '  {1:2}',
             '[1, 2,]',
             '1.34.4e',
             '   true',
             '  false',
             '   null',
             '[null]',
             '[{"a": "basdf",\n "b": [1, 2]}, '
             '{1, 2:::,,,333444, "asd}}[[]][f", 123, 134-134e3413E+387}, '
             '"asdf", 1341234, null]',
             '["\\"}]]]}"]',
             'aadf]]',
             '[""]',
             '[["]"}',
             '[[]']
    for jstr in jstrs:
        res = get_json(jstr, start=0)
        print(res)

def __test():
    __test_get_json()

if __name__ == '__main__':
    __test()

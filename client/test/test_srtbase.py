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

import sys
from os import path

test_dir = path.dirname(__file__)
if test_dir == '':
    test_dir = '.'
test_dir = path.abspath(test_dir)
__base = path.basename(__file__)

src_dir = path.abspath("%s/.." % test_dir)

sys.path.insert(0, src_dir)

from srt_client.srtbase import *

class SrtTestBase(SrtBase):
    _conf = {'a': 3, 'b': 4}

class SrtTest1(SrtTestBase):
    _conf = {'c': 'dd', 'e': 444}

class SrtTest2(SrtTestBase):
    _conf = {'d': 'e'}

class SrtTestMul(SrtTest1, SrtTest2):
    _conf = {'a': 5}

def printall(*args):
    print(args)

def test():
    testbase = SrtTestBase()
    print(testbase._conf)
    test1 = SrtTest1()
    print(test1._conf)
    test2 = SrtTest1()
    print(test2._conf)
    testmul = SrtTestMul()
    print(testmul._conf)
    try:
        testmul.a = 3
        exit(1)
    except TypeError as err:
        print(err)
    testmul.h = 4
    print('testmul.a: %a' % testmul.a)
    print('testmul.h: %a' % testmul.h)
    print(testmul.conf)

    testmul.connect('update-conf', printall)
    testmul.connect('notify::conf', printall)
    testmul.update_conf({'a': 4, 'b': 9, 'g': 1000})
    print(testmul.conf)
    testmul.update_conf({'a': 4, 'b': 9, 'g': 100})
    print(testmul.conf)
    print(SRTERR_DISCONN,
          SRTERR_BUSY,
          SRTERR_MOVE_LIMIT,
          SRTERR_UNKNOWN_REPLY,
          SRTERR_UNKNOW_CMD)

if __name__ == '__main__':
    test()

#!/usr/bin/env python

import sys
from os import path

test_dir = path.dirname(__file__)
if test_dir == '':
    test_dir = '.'
test_dir = path.abspath(test_dir)
__base = path.basename(__file__)

src_dir = path.abspath("%s/.." % test_dir)

sys.path.insert(0, src_dir)

from srt_client import srtbase

class SrtTestBase(srtbase.SrtBase):
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

if __name__ == '__main__':
    test()

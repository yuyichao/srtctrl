#!/usr/bin/env python

import sys
from os import path

test_dir = path.dirname(__file__)
if test_dir == '':
    test_dir = '.'
test_dir = path.abspath(test_dir)
__base = path.basename(__file__)

src_dir = path.abspath("%s/../.." % test_dir)

sys.path.insert(0, src_dir)

from srt_comm.jsonstm import *

def __test_get_json():
    jstrs = ['     []',
             '     {}',
             '  {1:2}',
             '[1, 2,]',
             '1.34.4e',
             '   true',
             '  false',
             '   null',
             '[{"a": "basdf",\n "b": [1, 2]}, '
             '{1, 2:::,,,333444, "asd}}[[]][f", 123, 134-134e3413E+387}, '
             '"asdf", 1341234, null]']
    for jstr in jstrs:
        print(jstr)
        print(get_json(jstr, start=0))

def __test():
    __test_get_json()

if __name__ == '__main__':
    __test()

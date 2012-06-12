#!/usr/bin/env python

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
             '[null]',
             '[{"a": "basdf",\n "b": [1, 2]}, '
             '{1, 2:::,,,333444, "asd}}[[]][f", 123, 134-134e3413E+387}, '
             '"asdf", 1341234, null]']
    for jstr in jstrs:
        res = get_json(jstr, start=0)
        if res[1] != '':
            print(res)
            exit(1)

def __test():
    __test_get_json()

if __name__ == '__main__':
    __test()

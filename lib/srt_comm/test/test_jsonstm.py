#!/usr/bin/env python

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

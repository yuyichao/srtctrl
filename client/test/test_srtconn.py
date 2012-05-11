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

from srt_client.srtconn import *

def test():
    srtconn = SrtConnBase()
    print(srtconn.conf)

if __name__ == '__main__':
    test()

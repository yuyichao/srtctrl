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

from srt_client.srtconn import *

def test():
    srtconn = SrtConnBase()
    print(srtconn.conf)

if __name__ == '__main__':
    test()

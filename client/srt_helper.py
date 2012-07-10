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

from srt_comm import *

class SrtHelper:
    def __init__(self, sock):
        self._sock = sock
        self._plugins = SrtPlugins()
    def _run(self):
        pass
    def send(self, obj):
        self._sock.send(obj)
        self._sock.wait_send()
    def _recv(self):
        return self._sock.recv()
    def recv(self):
        while True:
            pkg = self._sock.recv()

def main():
    sock = get_passed_conns(gtype=JSONSock)[0]
    helper = SrtHelper(sock)
    helper._run()

if __name__ == '__main__':
    main()

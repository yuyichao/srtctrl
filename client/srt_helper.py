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
        self._name = None
        self.ready = False
        self._plugins = SrtPlugins()
    def check_pkg_type(self, pkg):
        try:
            pkgtype = pkg['type']
        except:
            return None
        return pkgtype
    def _start(self):
        while True:
            pkg = self._sock.recv()
            pkgtype = self.check_pkg_type(pkg)
            if pkgtype is None:
                continue
            elif pkgtype == "error":
                continue
            elif pkgtype == "init":
                try:
                    name = pkg["name"]
                except:
                    continue
                try:
                    self._plugins.helper[name](self)
                except:
                    self.send({"type": "error", "errno": SRTERR_PLUGIN,
                               "msg": "helper [%s] cannot be loaded" % name})
            elif pkgtype == "ready":
                self.ready = True
    def send(self, obj):
        self._sock.send(obj)
        self._sock.wait_send()
    def recv(self):
        while True:
            pkg = self._sock.recv()

def main():
    sock = get_passed_conns(gtype=JSONSock)[0]
    helper = SrtHelper(sock)
    helper._start()

if __name__ == '__main__':
    main()

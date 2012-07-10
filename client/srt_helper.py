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

# _exit = exit
# def exit():
#     print('exit')
#     _exit()

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
            if not pkg:
                exit()
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
                except Exception as err:
                    # print(err)
                    self._send({"type": "error", "errno": SRTERR_PLUGIN,
                                "msg": "error running helper [%s]" % name})
                return
            elif pkgtype == "ready":
                self.ready = True
            elif pkgtype == "quit":
                exit()
    def _send(self, obj):
        self._sock.send(obj)
        self._sock.wait_send()
    def send(self, obj):
        self._send({"type": "remote", "obj": obj})
    def reply(self, sid, obj):
        self._send({"type": "slave", "sid": sid, "obj": obj})
    def send_got_cmd(self, sid):
        self._send({"type": "got-cmd", "sid": sid})
    def send_busy(self, sid):
        self._send({"type": "busy", "sid": sid})
    def send_ready(self):
        self._send({"type": "ready"})
    def recv(self):
        while True:
            pkg = self._sock.recv()
            if not pkg:
                exit()
            pkgtype = self.check_pkg_type(pkg)
            if pkgtype is None:
                continue
            elif pkgtype == "init":
                # self._send({"type": "error", "errno": SRTERR_GENERIC_LOCAL,
                #             "msg": "trying to init helper multiple times"})
                continue
            elif pkgtype == "quit":
                exit()
            elif pkgtype == "error":
                continue
            elif pkgtype in ["ready", "remote", "slave"]:
                return pkg
            self._send({"type": "error", "errno": SRTERR_UNKNOWN_CMD,
                        "msg": "trying to init helper multiple times"})

def main():
    sock = get_passed_conns(gtype=JSONSock)[0]
    helper = SrtHelper(sock)
    try:
        helper._start()
    except:
        pass

if __name__ == '__main__':
    main()

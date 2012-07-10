# coding=utf-8

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

class ZwickyHelper:
    def __init__(self, helper):
        self._helper = helper
        self._ready = helper.ready
        self._pending_slave = None
        # init config here
    def recv(self):
        while True:
            pkg = self._helper.recv()
            pkgtype = pkg["type"]
            if pkgtype == "ready":
                continue
            elif pkgtype == "remote":
                obj = pkg["obj"]
                return self.handle_remote(obj)
            elif pkgtype == "slave":
                self.handle_slave(pkg["sid"], pkg["obj"])
            else:
                continue
    def recv_slave(self):
        if not self._pending_slave is None:
            sid, obj = self._pending_slave
            self._pending_slave = None
            self._helper.send_got_cmd(sid)
            return sid, obj
        else:
            while True:
                pkg = self._helper.recv()
                pkgtype = pkg["type"]
                if pkgtype == "ready":
                    continue
                elif pkgtype == "remote":
                    self.handle_remote(pkg["obj"])
                    continue
                elif pkgtype == "slave":
                    sid, obj = pkg["sid"], pkg["obj"]
                    self._helper.send_got_cmd(sid)
                    return (sid, obj)
                else:
                    continue

    def handle_remote(self, obj):
        # update coordinate etc and return processed data
        pass
    def handle_slave(self, sid, obj):
        if obj["type"] == "prop":
            self.handle_prop(sid, obj)
        else:
            if self._pending_slave is None:
                self._pending_slave = (sid, obj)
                return
            self._helper.send_busy(sid)
    def handle_prop(self, sid, obj):
        pass
    def send(self, obj):
        self._helper.send(obj)
        return self.recv()
    def reset(self):
        self.send({"type": "move", "direct": 0, "count": 5000})
        self.send({"type": "move", "direct": 2, "count": 5000})
        self.send({"type": "source", "on": False})
        # init coordinate here
    def wait_ready(self):
        if self._helper.ready:
            return
        while True:
            pkg = self._helper.recv()
            pkgtype = pkg["type"]
            if pkgtype == "ready":
                return
    def run(self):
        self.wait_ready()
        self.reset()
        self._helper.send_ready()
        while True:
            sid, obj = self.recv_slave()
            # do real work here...

def StartZwicky(helper):
    zwicky = ZwickyHelper(helper)
    zwicky.run()
    print("exit")

iface.helper.zwicky = StartZwicky

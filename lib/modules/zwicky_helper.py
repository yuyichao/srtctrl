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

from srt_comm import *

class ZwickyHelper:
    def __init__(self, helper):
        self._helper = helper
        self._helper.connect("config", self._config_update_cb)
        self._helper.connect("get", self._get_cb)
        self._config_dict = {}
        self.configs = self._helper.configs.zwicky
        self.plugins = self._helper.plugins.zwicky
        self._motor = self.plugins.motor(self)
        self.get_config("station")
        self.get_config("curv_corr")
        self._reset_coor()
    def _reset_coor(self):
        self._motor.reset()
        self._source = False
    def _config_update_cb(self, helper, field, name, value):
        self._config_dict[name] = value
    def get_config(self, key, notify=True, non_null=True):
        return self._helper.get_config("zwicky", key,
                                       notify=notify, non_null=non_null)
    def _get_cb(self, helper, name, sid):
        pass
    def recv(self):
        while True:
            pkg = self._helper.wait_types("remote")
            try:
                obj = pkg["obj"]
            except:
                continue
            return self.handle_remote(obj)
    def recv_slave(self):
        while True:
            pkg = self._helper.wait_types(["remote", "slave"])
            pkgtype = pkg["type"]
            if pkgtype == "remote":
                try:
                    self.handle_remote(pkg["obj"])
                except:
                    pass
                continue
            elif pkgtype == "slave":
                sid, obj = dict_get_fields(pkg, "sid", "obj")
                if None in [sid, obj]:
                    continue
                self._helper.send_got_cmd(sid)
                return (sid, obj)

    def handle_remote(self, obj):
        # update coordinate etc and return processed data
        pass
    def send(self, obj):
        self._helper.send(obj)
        return self.recv()
    def reset(self):
        self.send({"type": "move", "direct": 0, "count": 5000})
        self.send({"type": "move", "direct": 2, "count": 5000})
        self.send({"type": "source", "on": False})
        self._reset_coor()
    def run(self):
        self._helper.wait_ready()
        self.reset()
        self._helper.send_ready()
        # while True:
        #     sid, obj = self.recv_slave()
        #     # do real work here...

def StartZwicky(helper):
    zwicky = ZwickyHelper(helper)
    zwicky.run()

iface.helper.zwicky = StartZwicky

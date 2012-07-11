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
        self._helper.connect("prop", self._get_prop_cb)
        self._config_dict = {}
        self.configs = self._helper.configs.zwicky
        self.plugins = self._helper.plugins.zwicky
        self._motor = self.plugins.motor(self)
        self._radio = self.plugins.radio(self)
        self.get_config("station")
        self._reset_coor()
    def _reset_coor(self):
        self._motor.reset()
        self._source = False
    def _config_update_cb(self, helper, field, name, value):
        self._config_dict[name] = value
    def get_config(self, key, notify=True, non_null=True):
        return self._helper.get_config("zwicky", key,
                                       notify=notify, non_null=non_null)
    def _get_prop_cb(self, helper, name, sid):
        pass
    def recv(self):
        while True:
            pkg = self._helper.wait_types("remote")
            try:
                obj = pkg["obj"]
            except:
                continue
            obj = self.handle_remote(obj)
            if obj is None:
                continue
            return obj
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
                sid, obj = get_dict_fields(pkg, ["sid", "obj"])
                if None in [sid, obj]:
                    continue
                self._helper.send_got_cmd(sid)
                return (sid, obj)

    def handle_remote(self, obj):
        objtype = get_dict_fields(obj, "type")
        if objtype is None:
            return
        if objtype == "beep":
            return
        elif objtype == "source":
            self._source = bool(get_dict_fields(obj, "on"))
            self.send_signal("source", self._source)
            return obj
        elif objtype == "move":
            direct, count, edge = get_dict_fields(obj,
                                                  ["direct", "count", "edge"])
            if None in [direct, count, edge]:
                return
            self._motor.move(direct, count, edge)
            return obj
        elif objtype == "radio":
            return obj
        return
    def send(self, obj):
        self._helper.send(obj)
        return self.recv()
    def send_signal(self, name, value):
        self._helper.send_signal(name, value)
    def send_move(self, direct, count):
        count = int(count)
        count = count if count >= 0 else 0
        return self.send({"type": "move", "direct": int(direct),
                          "count": count})
    def send_source(self, on):
        return self.send({"type": "source", "on": on})
    def send_radio(self, freq, mode):
        self._motor.pos_chk()
        reply = self.send({"type": "radio", "freq": freq, "mode": mode})
        rtype, data = get_dict_fields(reply, ["type", "data"])
        if None in [rtype, data]:
            return
        return self._radio.corr_radio(data, mode)
    def reset(self):
        self.send_move(0, 5000)
        self.send_move(2, 5000)
        self.send_source(False)
        self._reset_coor()
    def run(self):
        self._helper.wait_ready()
        self.reset()
        self._helper.send_ready()
        self._motor.set_pos(15, 15)
        self._motor.set_pos(10, 10)
        self.send_radio(30000, 1)
        # while True:
        #     sid, obj = self.recv_slave()
        #     # do real work here...
        self.reset()

def StartZwicky(helper):
    zwicky = ZwickyHelper(helper)
    zwicky.run()

iface.helper.zwicky = StartZwicky

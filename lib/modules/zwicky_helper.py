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
import time as _time

class ZwickyHelper:
    def __init__(self, helper):
        self._helper = helper
        self._helper.connect("config", self._config_update_cb)
        self._helper.connect("prop", self._get_prop_cb)
        self._helper.connect("track", self._track_cb)
        self._config_dict = {}
        self.configs = self._helper.configs.zwicky
        self.plugins = self._helper.plugins.zwicky
        self._motor = self.plugins.motor(self)
        self._radio = self.plugins.radio(self)
        self._tracker = self.plugins.tracker(self)
        self.get_config("station")
        self._reset_coor()
    def _reset_coor(self):
        self._tracker.reset()
        self._motor.reset()
        self._source = False
    def _config_update_cb(self, helper, field, name, value):
        self._config_dict[name] = value
    def get_config(self, key, notify=True, non_null=True):
        return self._helper.get_config("zwicky", key,
                                       notify=notify, non_null=non_null)
    def _get_prop_cb(self, helper, name, sid):
        value = self.get_prop(name)
        helper.send_prop(sid, name, value)
    def _track_cb(self, helper, az, el):
        self._tracker.set_pos(az, el)
    def get_prop(self, name):
        if name == "pos":
            return [self._motor.az, self._motor.el]
        elif name == "track":
            # TODO
            pass
        elif name == "freq_mode":
            return self._radio.get_freq()
        elif name == "calib":
            return self._radio.get_calib()
        elif name == "sys_tmp":
            return self._radio.get_sys_tmp()
        elif name == "offset":
            return self._motor.get_offset()
        elif name == "gala_pos":
            pass
        elif name == "time":
            return _time.time()
        elif name == "source":
            return self._source
        elif name == "frange":
            pass
        return
    def get_all_props(self):
        prop_names = ["pos", "track", "freq_mode", "calib", "sys_tmp", "offset",
                      "gala_pos", "time", "source", "frange"]
        props = {}
        for pname in prop_names:
            props[pname] = self.get_prop(pname)
        return props
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
            pkg = self._helper.wait_types(["remote", "slave", "track"])
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
            elif pkgtype == "track":
                self._tracker.update_pos()

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
    def send_track(self, name, offset, time, abstime, track, args):
        self._helper.send_track(name, offset, time, abstime, track, args)
    def send_radio(self, freq, mode):
        self._tracker.update_pos()
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
        # self.move(15, 15)
        self.move(10, 10)
        print(self.radio())
        print(self.calib(3))
        print(self.radio())
        # while True:
        #     sid, obj = self.recv_slave()
        #     # do real work here...
        self.reset()

    def move(self, az, el):
        self._motor.set_pos(az, el)
    def set_freq(self, freq, mode):
        self._radio.set_freq(freq, mode)
    def get_freq(self):
        return self._radio.get_freq()
    def radio(self):
        return self._radio.radio()
    def calib(self, count):
        return self._radio.calib(count)
    def track(self, **kwargs):
        return self._tracker.track(**kwargs)

def StartZwicky(helper):
    zwicky = ZwickyHelper(helper)
    zwicky.run()

iface.helper.zwicky = StartZwicky

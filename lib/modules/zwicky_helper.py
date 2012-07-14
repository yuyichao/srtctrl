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
        self.plugins = self._helper.plugins.device.zwicky
        self.properties = self._helper.plugins.props.zwicky
        self.commands = self._helper.plugins.cmds.zwicky
        self.motor = self.plugins.motor(self)
        self.radio = self.plugins.radio(self)
        self.tracker = self.plugins.tracker(self)
        self.get_config("station")
        self._reset_coor()
    def _reset_coor(self):
        self.tracker.reset()
        self.motor.reset()
        self.source_on = False
    def _config_update_cb(self, helper, field, name, value):
        self._config_dict[name] = value
    def get_config(self, key, notify=True, non_null=True):
        return self._helper.get_config("zwicky", key,
                                       notify=notify, non_null=non_null)
    def _get_prop_cb(self, helper, name, sid):
        value = self.get_prop(name)
        helper.send_prop(sid, name, value)
    def _track_cb(self, helper, az, el):
        self.tracker.set_pos(az, el)
    def get_prop(self, name):
        try:
            return self.properties[name](self)
        except:
            return
    def get_all_props(self):
        props = {}
        for pname in self.properties:
            props[pname] = self.get_prop(pname)
        return props
    def recv(self):
        while True:
            pkg = self._helper.wait_types("remote")
            obj = self.handle_remote(pkg["obj"])
            if obj is None:
                continue
            return obj
    def recv_slave(self):
        while True:
            pkg = self._helper.wait_types(["remote", "slave", "track"])
            pkgtype = pkg["type"]
            if pkgtype == "remote":
                self.handle_remote(**pkg)
                continue
            elif pkgtype == "slave":
                self._helper.send_got_cmd(pkg["sid"])
                return pkg
            elif pkgtype == "track":
                self.tracker.update_pos()
    def _process_cmd(self, sid=None, name=None, args=[], kwargs={}, **kw):
        try:
            res = self.commands[name](self, *args, **kwargs)
        except:
            res = None
        if not res is None:
            self.send_invalid(sid)
        else:
            self.send_reply(sid, res)
    def _handle_source(self, on=None, **kw):
        self.source_on = bool(on)
        self.send_signal("source", self.source_on)
        return {"type": "source", "on": self.source_on}
    def _handle_move(self, direct=None, count=None, edge=None, **kw):
        if None in [direct, count, edge]:
            return
        try:
            direct = int(direct)
            count = int(count)
            edge = int(edge)
        except:
            return
        self.motor.move(direct, count, edge)
        return {"type": "move", "direct": direct, "count": count, "edge": edge}
    def handle_remote(self, obj=None, **kw):
        if obj is None:
            return
        objtype = get_dict_fields(obj, "type")
        if objtype is None:
            return
        if objtype == "beep":
            return
        elif objtype == "source":
            return self._handle_source(**obj)
        elif objtype == "move":
            return self._handle_move(**obj)
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
    def send_track(self, name, offset, time, track, args):
        self._helper.send_track(name, offset, time, track, args,
                                self.configs.station)
    def send_radio(self, freq, mode):
        self.tracker.update_pos()
        self.motor.pos_chk()
        reply = self.send({"type": "radio", "freq": freq, "mode": mode})
        rtype, data = get_dict_fields(reply, ["type", "data"])
        if None in [rtype, data]:
            return
        return self.radio.corr_radio(data, mode)
    def send_reply(self, sid, obj):
        self._helper.reply(sid, obj)
    def send_invalid(self, sid):
        self.send_reply(sid, {"type": "error", "errno": SRTERR_UNKNOWN_CMD,
                              "msg": "invalid request"})
    def reset(self):
        self.send_move(0, 5000)
        self.send_move(2, 5000)
        self.send_source(False)
        self._reset_coor()
    def run(self):
        self._helper.wait_ready()
        self.reset()
        self._helper.send_ready()
        while True:
            pkg = self.recv_slave()
            self._process_cmd(**pkg)
        self.reset()
    def move(self, az, el):
        self.motor.set_pos(az, el)

    def set_freq(self, freq, mode):
        self.radio.set_freq(freq, mode)
    def get_freq(self):
        return self.radio.get_freq()
    def calib(self, count):
        return self.radio.calib(count)
    def track(self, **kwargs):
        if self.tracker.track(**kwargs):
            pkg = self._helper.wait_types("track")
            return check_track(**pkg)
        return

def check_track(az=None, el=None, **kw):
    if None in [az, el]:
        return
    return True

def StartZwicky(helper):
    zwicky = ZwickyHelper(helper)
    zwicky.run()

setiface.helper.zwicky = StartZwicky

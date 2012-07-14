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
        self._helper.connect("config", self._config_cb)
        self._helper.connect("ready", self._ready_cb)
        self._helper.connect("remote", self._remote_cb)
        self._helper.connect("notify", self._notify_cb)
        self.configs = self._helper.configs.zwicky
        self.plugins = self._helper.plugins.device.zwicky
        self.motor = self.plugins.motor(self)
        self.radio = self.plugins.radio(self)
        # TODO
        self.tracker = self.plugins.tracker(self)
        self.get_config("station")
        self._reset_coor()
    def _reset_coor(self):
        # TODO
        self.tracker.reset()
        self.motor.reset()
        self.source_on = False

    def _ready_cb(self, helper):
        self.reset()
    def _config_cb(self, helper, field, name, value):
        pass
    def _remote_cb(self, helper, obj):
        self._handle_remote(obj)
    def _handle_remote(self, obj)
        objtype = get_dict_fields(obj, "type")
        if objtype is None:
            return
        if objtype == "beep":
            return self._handle_beep()
        elif objtype == "source":
            return self._handle_source(**obj)
        elif objtype == "move":
            return self._handle_move(**obj)
        elif objtype == "radio":
            return self._handle_radio(**obj)
    def _handle_beep(self, host="", **kw):
        self.send_signal("beep", host)
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
    def _handle_radio(self, data=None, **kw):
        if data is None:
            return
        return {"type": "radio", "data": data}

    def get_config(self, key, notify=True, non_null=True):
        return self._helper.get_config("zwicky", key,
                                       notify=notify, non_null=non_null)

    def send_remote(self, obj):
        self._helper.send_remote(obj)
        return self._helper.recv_remote()
    def send_signal(self, name, value):
        self._helper.send_signal(name, value)
    def send_move(self, direct, count):
        count = int(count)
        count = count if count >= 0 else 0
        return self.send_remote({"type": "move", "direct": int(direct),
                                 "count": count})
    def send_source(self, on):
        return self.send_remote({"type": "source", "on": on})
    # def send_track(self, name, offset, time, track, args):
    #     self._helper.send_track(name, offset, time, track, args,
    #                             self.configs.station)
    def send_radio(self, freq, mode):
        # self.tracker.update_pos()
        self.motor.pos_chk()
        reply = self.send_remote({"type": "radio", "freq": freq, "mode": mode})
        rtype, data = get_dict_fields(reply, ["type", "data"])
        if None in [rtype, data]:
            return
        return self.radio.corr_radio(data, mode)
    def send_slave(self, sid, obj):
        self._helper.send_slave(sid, obj)
    def send_invalid(self, sid):
        self._helper.send_invalid(sid)
    def reset(self):
        self.send_move(0, 5000)
        self.send_move(2, 5000)
        self.send_source(False)
        self._reset_coor()

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

# def check_track(az=None, el=None, **kw):
#     if None in [az, el]:
#         return
#     return True

setiface.helper.zwicky = ZwickyHelper

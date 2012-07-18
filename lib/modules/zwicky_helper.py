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

from __future__ import print_function, division
from srt_comm import *
import time as _time

from gi.repository import GObject

class ZwickyHelper(GObject.Object):
    __gsignals__ = {
        "config": (GObject.SignalFlags.RUN_FIRST,
                   GObject.TYPE_NONE,
                   (GObject.TYPE_STRING, GObject.TYPE_STRING,
                    GObject.TYPE_PYOBJECT)),
        "alarm": (GObject.SignalFlags.RUN_FIRST | GObject.SignalFlags.DETAILED,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT,
                   GObject.TYPE_PYOBJECT)),
        # "remote": (GObject.SignalFlags.RUN_FIRST,
        #            GObject.TYPE_NONE,
        #            (GObject.TYPE_PYOBJECT,)),
        "ready": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  ())
    }
    def __init__(self, helper):
        super(ZwickyHelper, self).__init__()
        self._helper = helper
        self.configs = self._helper.configs.zwicky
        self.plugins = self._helper.plugins.device.zwicky
        self.motor = self.plugins.motor(self)
        self.radio = self.plugins.radio(self)
        self.tracker = self.plugins.tracker(self)
        self.remote_busy = False
        self.motor.reset()
        self.source_on = False
        self._helper.connect("config", self._config_cb)
        self._helper.connect("ready", self._ready_cb)
        self._helper.connect("remote", self._remote_cb)
        self._helper.connect("alarm", self._alarm_cb)

    def __getattr__(self, name):
        if name == "cmd_busy":
            return self._helper.cmd_busy
        raise AttributeError
    # callbacks
    def _ready_cb(self, helper):
        self.reset()
        self.emit("ready")
    def _config_cb(self, helper, field, name, value):
        self.emit("config", field, name, value)
    def _remote_cb(self, helper, obj):
        self._handle_remote(obj)
    def _alarm_cb(self, helper, name, nid, alarm):
        self.emit("alarm::%s" % name.replace('_', '-'),
                  name, nid, alarm)

    # handles
    def _handle_remote(self, obj):
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
        self.remote_busy = False
        self.source_on = bool(on)
        self.send_signal("source", self.source_on)
        return {"type": "source", "on": self.source_on}
    def _handle_move(self, direct=None, count=None, edge=None, **kw):
        if None in [direct, count, edge]:
            return
        self.remote_busy = False
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
        self.remote_busy = False
        return {"type": "radio", "data": data}

    def wait_alarm(self):
        return self._helper.wait_alarm()
    def get_config(self, key, notify=True, non_null=True):
        return self._helper.get_config("zwicky", key,
                                       notify=notify, non_null=non_null)
    def send_remote(self, obj):
        self.remote_busy = True
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
    def send_radio(self, freq, mode):
        reply = self.send_remote({"type": "radio", "freq": freq, "mode": mode})
        rtype, data = get_dict_fields(reply, ["type", "data"])
        if None in [rtype, data]:
            return
        return self.radio.corr_radio(data, mode)
    def send_slave(self, sid, obj):
        self._helper.send_slave(sid, obj)
    def send_invalid(self, sid):
        self._helper.send_invalid(sid)
    def send_chk_alarm(self, name, nid, args):
        return self._helper.send_chk_alarm(name, nid, args)

    def reset(self):
        self.tracker.reset()
        self.send_move(0, 5000)
        self.send_move(2, 5000)
        self.motor.reset()
        self.send_source(False)
        self.source_on = False
    def move(self, az, el):
        self.motor.set_pos(az, el)
    def set_freq(self, freq, mode):
        self.radio.set_freq(freq, mode)
    def get_freq(self):
        return self.radio.get_freq()
    def calib(self, count):
        return self.radio.calib(count)
    def track(self, **kwargs):
        return self.tracker.track(**kwargs)

setiface.helper.zwicky = ZwickyHelper

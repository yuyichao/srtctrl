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
from gi.repository import GObject

# _exit = exit
# def exit():
#     print('exit')
#     _exit()

class SrtHelper(GObject.Object):
    __gsignals__ = {
        "config": (GObject.SignalFlags.RUN_FIRST,
                   GObject.TYPE_NONE,
                   (GObject.TYPE_STRING, GObject.TYPE_STRING,
                    GObject.TYPE_PYOBJECT)),
        "prop": (GObject.SignalFlags.RUN_FIRST,
                 GObject.TYPE_NONE,
                 (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
        "track": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_DOUBLE, GObject.TYPE_DOUBLE)),
    }
    def __init__(self, sock):
        super().__init__()
        self._sock = sock
        self._name = None
        self._ready = False
        self.plugins = SrtPlugins()
        self._config_cache = {}
        self.configs = new_wrapper2(lambda field, name:
                                    self.get_config(field, name, non_null=False),
                                    None)
        self._pkg_queue = []
    def wait_types(self, types):
        if isinstance(types, str):
            types = [types]
        for i in range(len(self._pkg_queue)):
            if self._pkg_queue[i]["type"] in types:
                return self._pkg_queue.pop(i)
        while True:
            pkg = self._sock.recv()
            if not pkg:
                exit()
            pkgtype = get_dict_fields(pkg, "type")
            if pkgtype is None:
                continue
            elif pkgtype == "quit":
                exit()
            # elif pkgtype == "error":
            #     continue
            elif pkgtype == "ready":
                self._ready = True
            elif pkgtype == "config":
                field, name, notify, value = get_dict_fields(pkg,
                                                             ["field", "name",
                                                              "notify", "value"])
                if None in (field, name, notify):
                    continue
                try:
                    field = str(field)
                    name = str(name)
                except:
                    continue
                if notify:
                    self._cache_config(field, name, value)
                self.emit("config", field, name, value)
            elif pkgtype == "prop":
                name, sid = get_dict_fields(pkg, ["name", "sid"])
                if None in (name, sid):
                    continue
                try:
                    name = str(name)
                except:
                    continue
                self.emit("prop", name, sid)
            elif pkgtype == "track":
                self._handle_track(pkg)
            if pkgtype in types:
                return pkg
            if pkgtype in ["config", "prop", "ready", "init", "error", "track"]:
                continue
            self._pkg_queue.append(pkg)
    def _handle_track(self, pkg):
        print("handle_track", pkg)
        az, el = get_dict_fields(pkg, ["az", "el"])
        if None in [az, el]:
            return
        try:
            az = float(az)
            el = float(el)
            self.emit("track", az, el)
        except:
            pass
    def _start(self):
        pkg = self.wait_types("init")
        name = get_dict_fields(pkg, "name")
        if name is None:
            return
        self.plugins.helper[name](self)
        # try:
        #     self.plugins.helper[name](self)
        # except Exception as err:
        #     print(err)
        #     self._send({"type": "error", "errno": SRTERR_PLUGIN,
        #                 "msg": "error running helper [%s]" % name})
        return
    def wait_ready(self):
        if self._ready:
            return
        self.wait_types("ready")
        return

    def _send(self, obj):
        self._sock.send(obj)
        self._sock.wait_send()
    def send(self, obj):
        self._send({"type": "remote", "obj": obj})
    def reply(self, sid, obj):
        self._send({"type": "slave", "sid": sid, "obj": obj})
    def send_got_cmd(self, sid):
        self._send({"type": "got-cmd", "sid": sid})
    # def send_busy(self, sid):
    #     self._send({"type": "busy", "sid": sid})
    def send_ready(self):
        self._send({"type": "ready"})
    def send_prop(self, sid, name, value):
        self._send({"type": "prop", "sid": sid,
                    "name": name, "value": value})
    def send_quit(self):
        self._send({"type": "quit"})
    def send_signal(self, name, value):
        self._send({"type": "signal", "name": name, "value": value})
    def send_track(self, name, offset, time, abstime, track, args, station):
        self._send({"type": "track", "name": name, "offset": offset,
                    "time": time, "abstime": bool(abstime),
                    "track": bool(track), "args": args, "station": station})

    def _cache_config(self, field, name, value):
        set_2_level(self._config_cache, field, name, value)
    def get_config(self, field, name, notify=True, non_null=True):
        try:
            return self._config_cache[field][name]
        except:
            pass
        self._send({"type": "config", "field": field, "name": name,
                    "notify": bool(notify)})
        pkg = self.wait_types("config")
        value = pkg["value"]
        if value is None and non_null:
            raise KeyError("config %s.%s not found" % (field, name))
        return pkg["value"]

def main():
    sock = get_passed_conns(gtype=JSONSock)[0]
    helper = SrtHelper(sock)
    helper._start()
    # try:
    #     helper._start()
    # except Exception as err:
    #     print(err)

if __name__ == '__main__':
    main()

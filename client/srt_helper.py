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
from gi.repository import GObject, GLib

class SrtHelper(GObject.Object):
    __gsignals__ = {
        "config": (GObject.SignalFlags.RUN_FIRST,
                   GObject.TYPE_NONE,
                   (GObject.TYPE_STRING, GObject.TYPE_STRING,
                    GObject.TYPE_PYOBJECT)),
        "alarm": (GObject.SignalFlags.RUN_FIRST | GObject.SignalFlags.DETAILED,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT,
                   GObject.TYPE_PYOBJECT)),
        "remote": (GObject.SignalFlags.RUN_FIRST,
                   GObject.TYPE_NONE,
                   (GObject.TYPE_PYOBJECT,)),
        "ready": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  ())
    }
    def __init__(self, sock):
        super().__init__()
        self._sock = sock
        self._name = None
        self._ready = False
        self._device = None
        self.plugins = SrtPlugins()
        self._config_cache = {}
        self.configs = new_wrapper2(lambda field, name:
                                    self.get_config(field, name, False),
                                    None)
        self._pkg_queue = []
        self._auto_props = True

    # Main Receive
    def wait_types(self, types):
        if isinstance(types, str):
            types = [types]
        for i in range(len(self._pkg_queue)):
            if self._pkg_queue[i]["type"] in types:
                return self._pkg_queue.pop(i)
        while True:
            try:
                pkg = self._sock.recv()
            except GLib.GError:
                exit()
            if not pkg:
                exit()
            pkgtype = get_dict_fields(pkg, "type")
            if pkgtype is None:
                continue
            elif pkgtype == "quit":
                exit()
            elif pkgtype == "ready":
                self._ready = True
                pkg = {"type": "ready"}
            elif pkgtype == "config":
                pkg = self._handle_config(**pkg)
            elif pkgtype == "prop":
                pkg = self._handle_prop(**pkg)
            elif pkgtype == "alarm":
                pkg = self._handle_alarm(**pkg)
            elif pkgtype == "slave":
                pkg = self._handle_slave(**pkg)
            elif pkgtype == "remote":
                pkg = self._handle_remote(**pkg)
            if pkg is None:
                continue
            if pkgtype in types:
                return pkg
            if pkgtype == "slave":
                self._pkg_queue.append(pkg)

    # handles
    def _handle_config(self, field=None, name=None, notify=False,
                       value=None, **kw):
        if not isinstance(name, str) or not isinstance(field, str) :
            return
        notify = bool(notify)
        if notify:
            self._cache_config(field, name, value)
        self.emit("config", field, name, value)
        return {"type": "config", "notify": notify,
                "field": field, "name": name, "value": value}
    def _handle_prop(self, name=None, sid=None, **kw):
        if not isinstance(name, str) or self._name is None:
            self.send_invalid(sid)
            return
        try:
            value = self.plugins.props[name](self._device)
        except Exception as err:
            print(err)
            self.send_invalid(sid)
            return
        self.send_prop(sid,  name, value)
        return {"type": "prop", "name": name, "sid": sid}
    def _handle_alarm(self, name=None, nid=None, alarm=None,
                      success=None, **kw):
        if not isinstance(name, str) or not name.isidentifier():
            return
        if not success is None:
            return {"type": "alarm", "name": name, "nid": nid,
                    "success": bool(success)}
        self.emit("alarm::%s" % name.replace('_', '-'),
                  name, nid, alarm)
        return {"type": "alarm", "name": name, "nid": nid,
                "alarm": alarm}
    def _handle_slave(self, sid=None, name=None, args=[], kwargs={}, **kw):
        if name is None:
            self.send_invalid(sid)
            return
        try:
            args = list(args)
        except:
            args = []
        try:
            kwargs = dict(kwargs)
        except:
            kwargs = {}
        return {"type": "slave", "name": name, "sid": sid,
                "args": args, "kwargs": kwargs}
    def _handle_remote(self, obj=None, **kw):
        if obj is None:
            return
        self.emit("remote", obj)
        return {"type": "remote", "obj": obj}

    def get_all_props(self):
        if self._name is None or self._device is None:
            return {}
        try:
            props_plugins = self.plugins.props[self._name]
        except Exception as err:
            return {}
        props = {}
        for name in props_plugins:
            try:
                props[name] = props_plugins[name](self._device)
            except Exception as err:
                print(err)
        return props
    # receive utils
    def wait_ready(self):
        if self._ready:
            return
        self.wait_types("ready")
    def wait_alarm(self):
        return self.wait_types("alarm")
    def recv_remote(self):
        pkg = self.wait_types("remote")
        return pkg["obj"]
    def recv_slave(self):
        pkg = self.wait_types("slave")
        self.send_got_cmd(pkg["sid"])
        return pkg
    def send_chk_alarm(self, name, nid, args):
        if not (isinstance(name, str) and name.isidentifier()):
            return
        if not isinstance(args, dict):
            return
        if (isinstance(nid, list) or isinstance(nid, tuple)
            or isinstance(nid, dict)):
            return
        self.send_alarm(name, nid, args)
        while True:
            pkg = self.wait_alarm()
            if pkg["name"] != name or pkg["nid"] != nid:
                continue
            if "success" in pkg:
                if pkg["success"]:
                    return pkg
                return
            if pkg["alarm"] is None:
                return
            return pkg

    def start(self):
        pkg = self.wait_types("init")
        name = get_dict_fields(pkg, "name")
        if name is None:
            return
        self._name = name
        try:
            self._device = self.plugins.helper[name](self)
        except Exception as err:
            print(err)
            self._send({"type": "error", "errno": SRTERR_PLUGIN,
                        "msg": "error running helper [%s]" % name})
        self.wait_ready()
        self.emit("ready")
        self.send_ready()
        while True:
            pkg = self.recv_slave()
            self.exec_cmd(**pkg)

    def exec_cmd(self, sid=None, name=None, args=[], kwargs={}, **kw):
        try:
            res = self.plugins.cmds[name](self._device, *args, **kwargs)
        except:
            self.send_invalid(sid)
            return
        if self._auto_props:
            self.send_slave(sid, {"type": "res", "res": res,
                                  "props": self.get_all_props()})
        else:
            self.send_slave(sid, {"type": "res", "res": res})

    # sends
    def _send(self, obj):
        self._sock.send(obj)
        self._sock.wait_send()
    def send_remote(self, obj):
        self._send({"type": "remote", "obj": obj})
    def send_slave(self, sid, obj):
        self._send({"type": "slave", "sid": sid, "obj": obj})
    def send_invalid(self, sid):
        self.send_slave(sid, {"type": "error", "errno": SRTERR_UNKNOWN_CMD,
                              "msg": "invalid request"})
    def send_got_cmd(self, sid):
        self._send({"type": "got-cmd", "sid": sid})
    def send_ready(self):
        self._send({"type": "ready"})
    def send_prop(self, sid, name, value):
        self._send({"type": "prop", "sid": sid,
                    "name": name, "value": value})
    def send_quit(self):
        self._send({"type": "quit"})
    def send_signal(self, name, value):
        if self._auto_props:
            self._send({"type": "signal", "name": name, "value": value,
                        "props": self.get_all_props()})
        else:
            self._send({"type": "signal", "name": name, "value": value})
    def send_alarm(self, name, nid, args):
        self._send({"type": "alarm", "name": name, "nid": nid, "args": args})

    # config
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
    def set_auto_props(self, auto_props):
        self._auto_props = bool(auto_props)

def main():
    sock = get_passed_conns(gtype=JSONSock)[0]
    helper = SrtHelper(sock)
    helper.start()
    # try:
    #     helper._start()
    # except Exception as err:
    #     print(err)

if __name__ == '__main__':
    main()

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

from __future__ import print_function, division
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
        super(SrtHelper, self).__init__()
        self.cmd_busy = False
        self._sock = sock
        self._name = None
        self._ready = False
        self._device = None
        self.plugins = SrtPlugins()
        self._config_cache = {}
        self.configs = new_wrapper2(lambda field, name:
                                    self.get_config(field, name, False),
                                    None)
        self._slave_queue = []
        self._auto_props = True
        self._wait_queue = []

    # Main Receive
    def _push_cb(self, cb, check_only):
        index = len(self._wait_queue)
        obj = {"cb": cb, "check_only": check_only}
        if not check_only:
            for i in range(len(self._slave_queue)):
                try:
                    if cb(self._slave_queue[i]):
                        obj["res"] = self._slave_queue.pop(i)
                        break
                except:
                    pass
        self._wait_queue.append(obj)
        return index
    def _push_package(self, index, pkg):
        if index >= len(self._wait_queue):
            return
        self._wait_queue[:] = self._wait_queue[:index + 1]
        taken = False
        used = False
        for obj in self._wait_queue:
            if "res" in obj:
                continue
            if taken and not obj["check_only"]:
                continue
            try:
                if not obj["cb"](pkg):
                    continue
            except:
                continue
            obj["res"] = pkg
            used = True
            if not obj["check_only"]:
                taken = True
        if not used and "type" in pkg and pkg["type"] == "slave":
            printr("pushed", pkg)
            self._slave_queue.append(pkg)
        return used
    def _try_get_package(self, index):
        if index >= len(self._wait_queue):
            return
        self._wait_queue[:] = self._wait_queue[:index + 1]
        if "res" in self._wait_queue[-1]:
            return self._wait_queue[-1]["res"]
        return
    def wait_with_cb(self, cb, check_only=False):
        if not hasattr(cb, '__call__'):
            raise TypeError("cb is not callable")
        check_only = bool(check_only)
        index = self._push_cb(cb, check_only)
        while True:
            res = self._try_get_package(index)
            if res:
                return res
            try:
                pkg = self._sock.recv()
            except GLib.GError:
                exit()
            if not pkg:
                exit()
            try:
                pkg = self.__check_packages(**pkg)
            except:
                continue
            if pkg is None:
                continue
            self._push_package(index, pkg)
            try:
                self.__package_action(**pkg)
            except:
                pass
    def wait_types(self, types, check_only=False):
        if isstr(types):
            types = [types]
        return self.wait_with_cb(lambda pkg: (pkg["type"] in types),
                                 check_only)

    def __check_packages(self, type=None, **pkg):
        if type is None:
            return
        elif type == "quit":
            exit()
        elif type == "ready":
            self._ready = True
            return {"type": "ready"}
        elif type == "config":
            return self._check_config(**pkg)
        elif type == "init":
            return self._check_init(**pkg)
        elif type == "prop":
            return self._check_prop(**pkg)
        elif type == "alarm":
            return self._check_alarm(**pkg)
        elif type == "slave":
            return self._check_slave(**pkg)
        elif type == "remote":
            return self._check_remote(**pkg)
        return
    def __package_action(self, type=None, **pkg):
        if type is None:
            return
        elif type == "config":
            return self._config_action(**pkg)
        elif type == "init":
            return self._init_action(**pkg)
        elif type == "prop":
            return self._prop_action(**pkg)
        elif type == "alarm":
            return self._alarm_action(**pkg)
        elif type == "slave":
            return self._slave_action(**pkg)
        elif type == "remote":
            return self._remote_action(**pkg)
        return

    # handles
    def _check_init(self, name=None, **kw):
        return {"type": "init", "name": name}
    def _check_config(self, field=None, name=None, notify=False,
                      value=None, **kw):
        if not isstr(name) or not isstr(field) :
            return
        return {"type": "config", "notify": bool(notify),
                "field": field, "name": name, "value": value}
    def _check_prop(self, name=None, sid=None, **kw):
        if not isstr(name) or self._name is None:
            self.send_invalid(sid)
            return
        return {"type": "prop", "name": name, "sid": sid}
    def _check_alarm(self, name=None, nid=None, alarm=None,
                     success=None, **kw):
        if not isidentifier(name):
            return
        if not success is None:
            return {"type": "alarm", "name": name, "nid": nid,
                    "success": bool(success)}
        return {"type": "alarm", "name": name, "nid": nid,
                "alarm": alarm}
    def _check_slave(self, sid=None, name=None, args=[], kwargs={}, **kw):
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
    def _check_remote(self, obj=None, **kw):
        if obj is None:
            return
        return {"type": "remote", "obj": obj}

    def _init_action(self, name=None, **kw):
        if self._name is None:
            self._name = name
    def _config_action(self, field=None, name=None, notify=False,
                       value=None, **kw):
        if notify:
            self._cache_config(field, name, value)
        self.emit("config", field, name, value)
    def _prop_action(self, name=None, sid=None, **kw):
        try:
            value = self.plugins.props[self._name][name](self._device)
        except Exception as err:
            print_except()
            self.send_invalid(sid)
            return
        self.send_prop(sid,  name, value)
    def _alarm_action(self, name=None, nid=None, alarm=None,
                      success=None, **kw):
        if not success is None:
            return
        self.emit("alarm::%s" % name.replace('_', '-'),
                  name, nid, alarm)
    def _slave_action(self, sid=None, name=None, args=[], kwargs={}, **kw):
        pass
    def _remote_action(self, obj=None, **kw):
        self.emit("remote", obj)

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
                print_except()
        return props
    # receive utils
    def wait_ready(self):
        if self._ready:
            return
        self.wait_types("ready")
    def recv_remote(self):
        pkg = self.wait_types("remote")
        return pkg["obj"]
    def recv_slave(self):
        pkg = self.wait_types("slave")
        self.send_got_cmd(pkg["sid"])
        return pkg
    def send_chk_alarm(self, name, nid, args):
        if not isidentifier(name):
            return
        if not isinstance(args, dict):
            return
        if (isinstance(nid, list) or isinstance(nid, tuple)
            or isinstance(nid, dict)):
            return
        self.send_alarm(name, nid, args)
        res = self.wait_with_cb(
            lambda pkg: (pkg["type"] == "alarm" and
                         pkg["name"] == name and
                         pkg["nid"] == nid and
                         "success" in pkg))
        if res["success"]:
            return res
        return

    def start(self):
        self.send_chk_alarm("timer", "std", {})
        if self._name is None:
            pkg = self.wait_types("init")
        if self._name is None:
            return
        try:
            self._device = self.plugins.helper[self._name](self)
        except Exception as err:
            print_except()
            self._send({"type": "error", "errno": SRTERR_PLUGIN,
                        "msg": "error running helper [%s]" % self._name})
            return
        self.wait_ready()
        self.emit("ready")
        self.send_ready()
        while True:
            pkg = self.recv_slave()
            self._exec_cmd(**pkg)

    def _exec_cmd(self, sid=None, name=None, args=[], kwargs={}, **kw):
        self.cmd_busy = True
        try:
            res = self.plugins.cmds[self._name][name](self._device,
                                                      *args, **kwargs)
        except Exception as err:
            self.cmd_busy = False
            print_except()
            self.send_invalid(sid)
            return
        self.cmd_busy = False
        if self._auto_props:
            self.send_slave(sid, {"type": "res", "name": name, "res": res,
                                  "props": self.get_all_props()})
        else:
            self.send_slave(sid, {"type": "res", "name": name, "res": res})

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
    def set_config(self, field, name, value):
        self._send({"type": "config", "field": field, "name": name,
                    "set_value": True, "value": value})
    def set_auto_props(self, auto_props):
        self._auto_props = bool(auto_props)

def main():
    sock = get_passed_conns(gtype=JSONSock)[0]
    helper = SrtHelper(sock)
    try:
        helper.start()
    except Exception as err:
        print_except()

if __name__ == '__main__':
    main()

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
from gi.repository import GObject, GLib

# track, connect

class SrtHost(GObject.Object):
    __gsignals__ = {
        "quit": (GObject.SignalFlags.RUN_FIRST,
                 GObject.TYPE_NONE,
                 ()),
        "prop": (GObject.SignalFlags.RUN_FIRST,
                 GObject.TYPE_NONE,
                 (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING)),
        "query": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING)),
        "cmd": (GObject.SignalFlags.RUN_FIRST,
                GObject.TYPE_NONE,
                (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING,
                 GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
        "config": (GObject.SignalFlags.RUN_FIRST,
                   GObject.TYPE_NONE,
                   (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING,
                    GObject.TYPE_STRING, GObject.TYPE_BOOLEAN)),
        "set-config": (GObject.SignalFlags.RUN_FIRST,
                       GObject.TYPE_NONE,
                       (GObject.TYPE_STRING, GObject.TYPE_STRING,
                        GObject.TYPE_PYOBJECT)),
    }
    def __init__(self, plugins=None):
        super(SrtHost, self).__init__()
        if not plugins is None:
            self._plugins = plugins
        else:
            self._plugins = SrtPlugins()
        self._unique_id = 0
        self._slaves = {}
        self._lookup_id = {}
        self._name = None
        self._ready = False
        self.__init_cmd__()
        GLib.timeout_add_seconds(30, self._ping_lock_cb)
        GLib.timeout_add_seconds(600, self._ping_everyone_cb)
    def __init_cmd__(self):
        self._lock = -1
        self._processing = False
        self._cmd_queue = []
    def _new_usid(self):
        self._unique_id += 1
        return self._unique_id
    def _find_sid(self, slave):
        try:
            sid = self._lookup_id[id(slave)]
            if sid in self._slaves:
                return sid
        except:
            pass
    def add_slave_from_jsonsock(self, sock):
        if not isinstance(sock, JSONSock):
            return False
        if not sock.start_send() or not sock.start_recv():
            return False
        sock.connect('got-obj', self._slave_got_obj_cb)
        sock.connect('disconn', self._slave_disconn_cb)
        if not self._name is None:
            sock.send({"type": "init", "name": self._name})
        if self._ready:
            sock.send({"type": "ready"})
        sid = self._new_usid()
        self._slaves[sid] = {"sock": sock, "alarms": {},
                             "ping": None, "float": False}
        self._lookup_id[id(sock)] = sid
        return True
    def create_slave_by_name(self, name, pwd, args):
        try:
            if self._plugins.slave[name](self, pwd, **args):
                return True
        except Exception as err:
            print_except()
        return False
    def _process_cmd(self, type=None, sid=None, lock=False,
                     name=None, args=None, kwargs=None, **kw):
        if self._processing:
            return
        if None in [type, sid]:
            return
        if self._lock >= 0 and not sid == self._lock:
            return
        if type == "lock":
            if lock:
                self._lock = sid
                self._send_sid(sid, {"type": "lock", "res": True})
                self._check_queue()
            else:
                self._lock = -1
                self._check_queue()
            return True
        elif type == "cmd":
            if name is None:
                return
            self.emit("cmd", sid, name, args, kwargs)
            return True
        return
    def _check_float(self):
        for sid, obj in self._slaves.items():
            try:
                if not obj["float"]:
                    return
            except:
                pass
        self.emit("quit")
    def _check_queue(self):
        if self._processing:
            return
        if not self._cmd_queue:
            return
        if self._lock < 0:
            if self._process_cmd(**self._cmd_queue.pop(0)) is None:
                self._check_queue()
            return
        for i in range(len(self._cmd_queue)):
            cmd = self._cmd_queue[i]
            if cmd["sid"] == self._lock:
                if self._process_cmd(**self._cmd_queue.pop(i)) is None:
                    self._check_queue()
                return
        self._ping_sid(self._lock)
    def _slave_got_obj_cb(self, slave, pkg):
        pkgtype = get_dict_fields(pkg, "type")
        sid = self._find_sid(slave)
        try:
            self._clear_ping(sid)
        except:
            pass
        if sid is None:
            self._send_invalid(slave)
            return
        res = None
        if pkgtype == "config":
            res = self._handle_config(sid, **pkg)
        elif pkgtype == "start":
            res = self._handle_start(sid, **pkg)
        # elif pkgtype == "name":
        #     res = self._handle_name(sid, **pkg)
        elif pkgtype == "float":
            res = self._handle_float(sid, **pkg)
        elif pkgtype == "prop":
            res = self._handle_prop(sid, **pkg)
        elif pkgtype == "slave-error":
            res = self._handle_slave_error(sid, **pkg)
        elif pkgtype == "query":
            res = self._handle_query(sid, **pkg)
        elif pkgtype == "pong":
            res = self._handle_pong(sid, **pkg)
        elif pkgtype == "cmd":
            res = self._handle_cmd(sid, **pkg)
        elif pkgtype == "lock":
            res = self._handle_lock(sid, **pkg)
        elif pkgtype == "quit":
            res = self._handle_quit(sid, **pkg)
        elif pkgtype == "alarm":
            res = self._handle_alarm(sid, **pkg)
        if res is None:
            self._send_invalid(slave)
    def _ping_sid_cb(self, sid):
        if (not sid in self._slaves) or self._slaves[sid]["ping"] is None:
            return False
        try:
            self._slaves[sid]["sock"].close()
        except:
            pass
        try:
            del self._slaves[sid]
        except:
            pass
        self._check_float()
        return False
    def _ping_lock_cb(self):
        try:
            self._ping_sid(self._lock)
        except:
            pass
        return True
    def _ping_everyone_cb(self):
        try:
            for sid in self._slaves:
                self._ping_sid(sid)
        except:
            pass
        return True
    def _clear_ping(self, sid):
        if not sid in self._slaves:
            return True
        if self._slaves[sid]["ping"] is None:
            return True
        try:
            GLib.source_remove(self._slaves[sid]["ping"])
        except:
            pass
        self._slaves[sid]["ping"] = None
        return True
    def _ping_sid(self, sid):
        if not sid in self._slaves:
            return
        if not self._slaves[sid]["ping"] is None:
            return
        self._slaves[sid]["ping"] = GLib.timeout_add_seconds(
            15, self._ping_sid_cb, sid)
        self._send_sid(sid, {"type": "ping"})
    def _send_invalid(self, slave):
        slave.send({"type": "error", "errno": SRTERR_UNKNOWN_CMD,
                    "msg": "invalid request"})
    def _send_sid(self, sid, pkg):
        try:
            slave = self._slaves[sid]["sock"]
        except:
            return
        slave.send(pkg)
        return True
    def _broadcast(self, pkg, wait=False):
        for sid, slave in self._slaves.items():
            try:
                slave["sock"].send(pkg)
                if wait:
                    slave["sock"].wait_send()
            except:
                pass
    def _handle_quit(self, sid, **kw):
        self.emit("quit")
        return True
    def _handle_alarm(self, sid, name="", nid=None, args={}, **kw):
        if (not (isidentifier(name) and isinstance(args, dict))
            or isinstance(nid, list) or isinstance(nid, dict)):
            self._send_sid(sid, {"type": "alarm", "name": name, "nid": nid,
                                 "success": False})
            return True
        if not name in self._slaves[sid]["alarm"]:
            self._slaves[sid]["alarm"][name] = {}
        try:
            alarm = self._plugins.alarm[name](**args)
            alarm.connect("alarm", self._slave_alarm_cb, name, nid, sid)
        except Exception as err:
            print_except()
            self._send_sid(sid, {"type": "alarm", "name": name, "nid": nid,
                                 "success": False})
            return True
        self._send_sid(sid, {"type": "alarm", "name": name, "nid": nid,
                             "success": True})
        try:
            self._slaves[sid]["alarm"][name][nid].stop()
        except:
            pass
        self._slaves[sid]["alarm"][name][nid] = alarm
        return True
    def _try_lock(self, sid):
        if self._lock == sid:
            return True
        if not self._lock < 0:
            return False
        if self._processing:
            return False
        for cmd in self._cmd_queue:
            if not cmd["sid"] == sid:
                return False
        self._lock = sid
        return True
    def _handle_lock(self, sid, wait=True, lock=None, **kw):
        if lock is None:
            return
        if not lock:
            self._cmd_queue.append({"type": "lock", "sid": sid,
                                    "lock": False})
            self._check_queue()
            return True
        wait = bool(wait)
        if self._try_lock(sid):
            self._send_sid(sid, {"type": "lock", "res": True})
            return True
        if not wait:
            self._send_sid(sid, {"type": "lock", "res": False})
            return True
        self._cmd_queue.append({"type": "lock", "sid": sid, "lock": True})
        self._check_queue()
        return True
    def _handle_cmd(self, sid, name=None, args=None, kwargs=None, **kw):
        if not isstr(name):
            return
        self._cmd_queue.append({"type": "cmd", "sid": sid, "name": name,
                                "args": args, "kwargs": kwargs})
        self._check_queue()
        return True
    def _handle_pong(self, sid, **kw):
        self._clear_ping(sid)
        return True
    def _handle_prop(self, sid, name=None, **kw):
        if not isstr(name):
            return
        if name == "name":
            self._send_sid(sid, {"type": "prop", "name": "name",
                                 "value": self._name})
            return True
        self.emit("prop", sid, name)
        return True
    def _handle_slave_error(self, sid, name=None, msg="", **kw):
        self._broadcast({"type": "slave-error", "name": name, "msg": msg})
        return True
    def _handle_query(self, sid, name=None, **kw):
        if not isstr(name):
            return
        self.emit("query", sid, name)
        return True
    def _handle_float(self, sid, float=True, **kw):
        try:
            self._slaves[sid]["float"] = bool(float)
        except:
            pass
        self._check_float()
        return True
    # def _handle_name(self, sid, **kw):
    #     return True
    def _handle_start(self, sid, name=None, pwd='.', args={}, **kw):
        if name is None:
            return
        args = std_arg({}, args)
        if not self.create_slave_by_name(name, pwd, args):
            return
        return True
    def _handle_config(self, sid, field=None, name=None, notify=False,
                       set_value=None, value=None, **kw):
        if not isstr(field) or not isstr(name):
            return
        if set_value:
            self.emit("set-config", field, name, value)
            self._send_sid(sid, {"type": "config", "field": field, "name": name,
                                 "set_value": True, "success": True})
            return True
        notify = bool(notify)
        self.emit("config", sid, field, name, notify)
        return True
    def _slave_alarm_cb(self, obj, alarm, name, nid, sid):
        if not isinstance(alarm, dict):
            return
        self._send_sid(sid, {"type": "alarm", "name": name,
                             "nid": nid, "alarm": alarm})
    def _slave_disconn_cb(self, slave):
        try:
            sid = self._lookup_id[id(slave)]
        except:
            return
        try:
            del self._lookup_id[id(slave)]
        except:
            pass
        try:
            GLib.source_remove(self._slaves[sid]["ping"])
        except:
            pass
        try:
            del self._slaves[sid]
        except:
            pass
        self._check_float()
        self._cmd_queue[:] = [cmd for cmd in self._cmd_queue
                              if not cmd["sid"] == sid]
        if self._lock == sid:
            self._lock = -1
        self._check_queue()
    def feed_prop(self, sid, name, value):
        return self._send_sid(sid, {"type": "prop",
                                    "name": name, "value": value})
    def feed_query(self, sid, name, name_list):
        return self._send_sid(sid, {"type": "query",
                                    "name": name, "name_list": name_list})
    def feed_got_cmd(self, sid):
        self._processing = False
        res = self._send_sid(sid, {"type": "cmd"})
        self._check_queue()
        return res
    def feed_config(self, sid, field, name, value, notify):
        return self._send_sid(sid, {"type": "config", "field": field,
                                    "name": name, "value": value,
                                    "notify": notify})
    def feed_res(self, sid, obj):
        objtype = get_dict_fields(obj, "type")
        if objtype is None:
            return
        elif objtype == "res":
            self._handle_feed_res(sid, **obj)
            return
        elif objtype == "error":
            self._handle_feed_error(sid, **obj)
            return
    def _handle_feed_res(self, sid, name=None, res=None, props={},
                         args=[], kwargs={}, **kw):
        if not isinstance(props, dict):
            props = {}
        self._send_sid(sid, {"type": "res", "name": name,
                             "args": args, "kwargs": kwargs,
                             "res": res, "props": props})
    def _handle_feed_error(self, sid, errno=None, msg=None, **kw):
        try:
            errno = int(errno)
        except:
            return
        msg = std_arg("", msg)
        self._send_sid(sid, {"type": "error", "errno": errno, "msg": msg})
    def feed_signal(self, name, value, props):
        self._broadcast({"type": "signal", "name": name,
                         "value": value, "props": props})
    # DO NOT emit "quit" signal here
    def quit(self):
        self._broadcast({"type": "quit"}, wait=True)
    def init(self, name):
        self._name = name
        self._broadcast({"type": "init", "name": name})
    def ready(self):
        self._ready = True
        self._broadcast({"type": "ready"})

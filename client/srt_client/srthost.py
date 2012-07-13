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
from gi.repository import GObject

# track, connect

class SrtHost(GObject.Object):
    __gsignals__ = {
        "quit": (GObject.SignalFlags.RUN_FIRST,
                 GObject.TYPE_NONE,
                 ()),
        "prop": (GObject.SignalFlags.RUN_FIRST,
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
    }
    def __init__(self):
        super().__init__()
        self._plugins = SrtPlugins()
        self._unique_id = 0
        self._slaves = {}
        self._lookup_id = {}
        self._name = None
        self._ready = False
        self.__init_cmd__()
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
        sid = self._new_usid()
        self._slaves[sid] = {"sock": sock, "signals": {}}
        self._lookup_id[id(sock)] = sid
        return True
    def create_slave_by_name(self, name, args):
        try:
            if self._plugins.slave[name](**args):
                return True
        except:
            pass
        return False
    def _process_cmd(self, type=None, sid=None, lock=False,
                     name=None, args=None, kwargs=None, **kw):
        if self._processing:
            return
        if None in [type, sid]:
            return
        if self._lock >= 0 and sid != self._lock:
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
    def _slave_got_obj_cb(self, slave, pkg):
        pkgtype = get_dict_fields(pkg, "type")
        sid = self._find_sid(slave)
        if sid is None:
            self._send_invalid(slave)
            return
        res = None
        if pkgtype == "connect":
            res = self._handle_connect(sid, **pkg)
        elif pkgtype == "config":
            res = self._handle_config(sid, **pkg)
        elif pkgtype == "start":
            res = self._handle_start(sid, **pkg)
        # elif pkgtype == "name":
        #     res = self._handle_name(sid, **pkg)
        elif pkgtype == "prop":
            res = self._handle_prop(sid, **pkg)
        elif pkgtype == "cmd":
            res = self._handle_cmd(sid, **pkg)
        elif pkgtype == "lock":
            res = self._handle_lock(sid, **pkg)
        elif pkgtype == "quit":
            res = self._handle_quit(sid, **pkg)
        # TODO make tracking a plugin
        elif pkgtype == "track":
            res = self._handle_track(sid, **pkg)
        if res is None:
            self._send_invalid(slave)
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
    def _handle_track(self, sid, **kw):
        # TODO
        return True
    def _try_lock(self, sid):
        if self._lock == sid:
            return True
        if not self._lock < 0:
            return False
        if self._processing:
            return False
        for cmd in self._cmd_queue:
            if cmd["sid"] != sid:
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
        if name is None:
            return
        if not isinstance(name, str):
            return
        self._cmd_queue.append({"type": "cmd", "sid": sid, "name": name,
                                "args": args, "kwargs": kwargs})
        self._check_queue()
        return True
    def _handle_prop(self, sid, name=None, **kw):
        if not isinstance(name, str):
            return
        if name == "name":
            self._send_sid(sid, {"type": "prop", "name": "name",
                                 "value": self._name})
            return True
        if name == "ready":
            self._send_sid(sid, {"type": "prop", "name": "ready",
                                 "value": self._ready})
            return True
        self.emit("prop", sid, name)
        return True
    # def _handle_name(self, sid, **kw):
    #     return True
    def _handle_start(self, sid, name=None, args={}, **kw):
        if name is None:
            return
        if not self.create_slave_by_name(name, args):
            return
        return True
    def _handle_config(self, sid, field=None, name=None, notify=False, **kw):
        if None in [field, name]:
            return
        if not isinstance(field, str) or not isinstance(name, str):
            return
        notify = bool(notify)
        self.emit("prop", sid, field, name, notify)
        return True
    def _handle_connect(self, sid, name=None, **kw):
        if not isinstance(name, str):
            return
        self._slaves[sid]["signals"][name] = name
        return True
    def _slave_disconn_cb(self, slave):
        try:
            sid = self._lookup_id[id(slave)]
        except:
            return
        try:
            del self._lookup_id[id(slave)]
            del self._slaves[sid]
        except:
            pass
        self._cmd_queue[:] = [cmd for cmd in self._cmd_queue
                              if not cmd["sid"] == sid]
        if self._lock == sid:
            self._lock = -1
        self._check_queue()
    def feed_prop(self, sid, name, value):
        return self._send_sid(sid, {"type": "prop",
                                    "name": name, "value": value})
    def feed_got_cmd(self, sid):
        self._processing = False
        res = self._send_sid(sid, {"type": "cmd"})
        self._check_queue()
        return res
    def feed_config(self, sid, field, name, value, notify):
        return self._send_sid(sid, {"type": "config", "name": name,
                                    "value": value, "notify": notify})
    def feed_res(self, sid, obj):
        return self._send_sid(sid, {"type": "res", "obj": obj})
    def feed_signal(self, name, value):
        for sid, slave in self._slaves.items():
            if name in slave["signals"]:
                self._send_sid(sid, {"type": "signal", "name": name,
                                     "value": value})
    # DO NOT emit "quit" signal here
    def quit(self):
        self._broadcast({"type": "quit"}, wait=True)
    def init(self, name):
        self._name = name
        self._broadcast({"type": "init", "name": name})
    def ready(self):
        self._ready = True
        self._broadcast({"type": "ready"})

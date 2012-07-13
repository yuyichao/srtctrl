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
                 GObject.TYPE_PYOBJECT)),
        "config": (GObject.SignalFlags.RUN_FIRST,
                   GObject.TYPE_NONE,
                   (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING,
                    GObject.TYPE_STRING, GObject.TYPE_BOOLEAN)),
    }
    def __init__(self):
        super().__init__()
        self._plugins = SrtPlugins()
        self._slaves = {}
        self._lock = -1
        self._cmd_queue = []
        self._name = None
        self._ready = False
    def add_slave_from_jsonsock(self, sock):
        if not isinstance(sock, JSONSock):
            return False
        if not sock.start_send() or not sock.start_recv():
            return False
        sock.connect('got-obj', self._slave_got_obj_cb)
        sock.connect('disconn', self._slave_disconn_cb)
        self._slaves[id(sock)] = {"sock": sock}
        return True
    def create_slave_by_name(self, name, args):
        try:
            if self._plugins.slave[name](**args):
                return True
        except:
            pass
        return False
    def _slave_got_obj_cb(self, slave, pkg):
        pkgtype = get_dict_fields(pkg, "type")
        # connect, config, start, name, prop, cmd, lock
        res = None
        if pkgtype == "connect":
            res = self._handle_connect(slave, **pkg)
        elif pkgtype == "config":
            res = self._handle_config(slave, **pkg)
        elif pkgtype == "start":
            res = self._handle_start(slave, **pkg)
        elif pkgtype == "name":
            res = self._handle_name(slave, **pkg)
        elif pkgtype == "prop":
            res = self._handle_prop(slave, **pkg)
        elif pkgtype == "cmd":
            res = self._handle_cmd(slave, **pkg)
        elif pkgtype == "lock":
            res = self._handle_lock(slave, **pkg)
        elif pkgtype == "quit":
            res = self._handle_lock(slave, **pkg)
        if res is None:
            slave.send({"type": "error", "errno": SRTERR_UNKNOWN_CMD,
                        "msg": "invalid request"})
    def _handle_quit(self, slave, **kw):
        pass
    def _handle_lock(self, slave, **kw):
        pass
    def _handle_cmd(self, slave, **kw):
        pass
    def _handle_prop(self, slave, **kw):
        pass
    def _handle_name(self, slave, **kw):
        pass
    def _handle_start(self, slave, **kw):
        pass
    def _handle_config(self, slave, **kw):
        pass
    def _handle_connect(self, slave, **kw):
        pass
    def _slave_disconn_cb(self, slave):
        try:
            del self._slaves[id(slave)]
        except:
            pass
        # TODO recheck
    def feed_prop(self, sid, name, value):
        pass
    def feed_got_cmd(self, sid):
        pass
    def feed_config(self, sid, field, name, value, notify):
        if not sid in self._slaves:
            return False
        # TODO
        return True
    def feed_res(self, sid, obj):
        pass
    def feed_signal(self, name, value):
        pass
    def quit(self):
        for sid, slave in self._slaves.items():
            try:
                slave.send({"type": "quit"})
                slave.wait_send()
            except:
                pass
    def init(self, name):
        self._name = name
    def ready(self):
        self._ready = True

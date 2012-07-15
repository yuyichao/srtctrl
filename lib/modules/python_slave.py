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

import sys
from srt_comm import *
from gi.repository import GObject, GLib

# requests: config, start, prop, cmd, lock, quit, alarm
# reply: error, alarm, lock, prop, init, ready, quit, config, cmd, res, signal

def new_iface(conn):
    _state = {"ready": False, "name": None}
    _config_cache = {}
    def _cache_config(field, name, value):
        set_2_level(_config_cache, field, name, value)
    def _handle_config(field=None, name=None, notify=False,
                       value=None, **kw):
        if not isinstance(name, str) or not isinstance(field, str) :
            return
        notify = bool(notify)
        if notify:
            _cache_config(field, name, value)
        iface.emit("config", field, name, value)
        return {"type": "config", "notify": notify,
                "field": field, "name": name, "value": value}
    def _handle_prop(name=None, value=None, **kw):
        return {"type": "prop", "name": name, "value": value}
    def _handle_alarm(name=None, nid=None, alarm=None,
                      success=None, **kw):
        if not isinstance(name, str) or not name.isidentifier():
            return
        if not success is None:
            return {"type": "alarm", "name": name, "nid": nid,
                    "success": bool(success)}
        if not alarm is None:
            iface.emit("alarm::%s" % name.replace('_', '-'),
                       name, nid, alarm)
        return {"type": "alarm", "name": name, "nid": nid,
                "alarm": alarm}
    def _handle_error(errno=None, msg=None, **kw):
        try:
            errno = int(errno)
        except:
            return
        msg = str(msg)
        return {"type": "error", "errno": errno, "msg": msg}
    def _handle_lock(res=None, **kw):
        return {"type": "lock", "res": bool(res)}
    def _handle_init(name=None, **kw):
        if not isinstance(name, str):
            return
        _state["name"] = name
        return {"type": "init", "name": name}
    def _handle_cmd(**kw):
        return {"type": "cmd"}
    def _handle_res(res=None, props={}, **kw):
        return {"type": "res", "res": res, "props": props}
    def _handle_signal(name=None, value=None, props={}, **kw):
        if not (isinstance(name, str) and name.isidentifier()):
            return
        props = std_arg({}, props)
        iface.emit("signal::%s" % name.replace('_', '-'),
                   name, value, props)
        return {"type": "res", "name": name, "value": value, "props": props}
    def wait_types(types):
        if isinstance(types, str):
            types = [types]
        while True:
            try:
                pkg = conn.recv()
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
                _state["ready"] = True
                pkg = {"type": "ready"}
            elif pkgtype == "config":
                pkg = _handle_config(**pkg)
            elif pkgtype == "prop":
                pkg = _handle_prop(**pkg)
            elif pkgtype == "alarm":
                pkg = _handle_alarm(**pkg)
            elif pkgtype == "error":
                pkg = _handle_error(**pkg)
            elif pkgtype == "lock":
                pkg = _handle_lock(**pkg)
            elif pkgtype == "init":
                pkg = _handle_init(**pkg)
            elif pkgtype == "cmd":
                pkg = _handle_cmd(**pkg)
            elif pkgtype == "res":
                pkg = _handle_res(**pkg)
            elif pkgtype == "signal":
                pkg = _handle_signal(**pkg)
            if pkg is None:
                continue
            if pkgtype in types:
                return pkg
    def send_quit():
        conn.send({"type": "quit"})
        conn.wait_send()
    def send_alarm():
        pass
    class PythonSlave(GObject.Object):
        __gsignals__ = {
            "config": (GObject.SignalFlags.RUN_FIRST,
                       GObject.TYPE_NONE,
                       (GObject.TYPE_STRING, GObject.TYPE_STRING,
                        GObject.TYPE_PYOBJECT)),
            "alarm": (GObject.SignalFlags.RUN_FIRST |
                      GObject.SignalFlags.DETAILED,
                      GObject.TYPE_NONE,
                      (GObject.TYPE_STRING, GObject.TYPE_STRING,
                       GObject.TYPE_PYOBJECT)),
            "signal": (GObject.SignalFlags.RUN_FIRST |
                       GObject.SignalFlags.DETAILED,
                       GObject.TYPE_NONE,
                       (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT,
                        GObject.TYPE_PYOBJECT)),
        }
        def __init__(self):
            super().__init__()
    iface = PythonSlave()
    return iface

def main():
    fname = sys.argv[1]
    sys.argv.pop(0)
    conn = get_passed_conns(gtype=JSONSock)[0]

def start_slave(host, fname=None, args=[], **kw):
    if not isinstance(fname, str):
        return False
    if (isinstance(args, str) or isinstance(args, float)
        or isinstance(args, int)):
        args = [str(args)]
    else:
        try:
            args = [str(arg) for arg in args]
        except:
            return False
    conn = exec_n_conn(sys.executable,
                       args=[sys.executable, __file__, fname] + args,
                       n=1, gtype=JSONSock)[0]
    return host.add_slave_from_jsonsock(self, sock)

if __name__ == '__main__':
    main()
elif 'setiface' in globals():
    setiface.slave.python = start_slave

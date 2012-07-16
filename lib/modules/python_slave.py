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

def new_iface(conn, sync=True):
    _state = {"ready": False, "name": None}
    sync = bool(sync)
    def got_obj_cb(conn, pkg):
        handle_pkg(pkg)
    def disconn_cb(conn):
        iface.emit("quit")
    if not sync:
        conn.start_send()
        conn.start_recv()
        conn.connect("got-obj", got_obj_cb)
        conn.connect("disconn", disconn_cb)
    def send(obj):
        conn.send(obj)
        if sync:
            conn.wait_send()
    def send_start(name, args={}):
        send({"type": "start", "name": name, "args": args})
    def send_prop(name):
        send({"type": "prop", "name": name})
        if not sync:
            return
        return wait_types(["prop", "error"])
    def send_cmd(name, *args, **kwargs):
        send({"type": "cmd", "name": name, "args": args, "kwargs": kwargs})
        if not sync:
            return
        wait_types("cmd")
        return wait_types(["error", "res"])
    def send_lock(lock, wait=True):
        lock = bool(lock)
        wait = bool(wait)
        send({"type": "lock", "lock": lock, "wait": wait})
        if not sync or not lock:
            return True
        pkg = wait_types("lock")
        if "res" in pkg and pkg["res"]:
            return True
        return
    def send_quit():
        send({"type": "quit"})
        iface.emit("quit")
    def send_alarm(name, nid="", **args):
        send({"type": "alarm", "name": name, "nid": nid, "args": args})
        if not sync:
            return
        while True:
            pkg = wait_types("alarm")
            if pkg["name"] != name or pkg["nid"] != nid:
                continue
            if "success" in pkg:
                if pkg["success"]:
                    return True
                return
            return True

    # config
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
    def get_config(field, name, notify=True, non_null=False):
        try:
            return _config_cache[field][name]
        except:
            pass
        send({"type": "config", "field": field, "name": name,
              "notify": bool(notify)})
        if not sync:
            return
        pkg = wait_types("config")
        value = pkg["value"]
        if value is None and non_null:
            raise KeyError("config %s.%s not found" % (field, name))
        return pkg["value"]

    def handle_pkg(pkg):
        if not pkg:
            iface.emit("quit")
        pkgtype = get_dict_fields(pkg, "type")
        if pkgtype is None:
            return
        elif pkgtype == "quit":
            iface.emit("quit")
            return {"type": "quit"}
        elif pkgtype == "ready":
            _state["ready"] = True
            iface.emit("ready")
            return {"type": "ready"}
        elif pkgtype == "config":
            return _handle_config(**pkg)
        elif pkgtype == "prop":
            return _handle_prop(**pkg)
        elif pkgtype == "alarm":
            return _handle_alarm(**pkg)
        elif pkgtype == "error":
            return _handle_error(**pkg)
        elif pkgtype == "lock":
            return _handle_lock(**pkg)
        elif pkgtype == "init":
            return _handle_init(**pkg)
        elif pkgtype == "cmd":
            return _handle_cmd(**pkg)
        elif pkgtype == "res":
            return _handle_res(**pkg)
        elif pkgtype == "signal":
            return _handle_signal(**pkg)
    def wait_types(types):
        if isinstance(types, str):
            types = [types]
        while True:
            try:
                pkg = conn.recv()
            except GLib.GError:
                iface.emit("quit")
            pkg = handle_pkg(pkg)
            if pkg is None:
                continue
            if pkgtype in types:
                return pkg
    def _handle_prop(name=None, value=None, **kw):
        iface.emit("prop", name, value)
        return {"type": "prop", "name": name, "value": value}
    def _handle_alarm(name=None, nid=None, alarm=None,
                      success=None, **kw):
        if not isinstance(name, str) or not name.isidentifier():
            return
        if not success is None:
            success = bool(success)
            iface.emit("alarm-success::%s" % name.replace('_', '-'),
                       name, nid, success)
            return {"type": "alarm", "name": name, "nid": nid,
                    "success": success}
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
        iface.emit("error", errno, msg)
        return {"type": "error", "errno": errno, "msg": msg}
    def _handle_lock(res=None, **kw):
        res = bool(res)
        iface.emit("lock", errno, res)
        return {"type": "lock", "res": res}
    def _handle_init(name=None, **kw):
        if not isinstance(name, str):
            return
        _state["name"] = name
        iface.emit("init", name)
        return {"type": "init", "name": name}
    def _handle_cmd(**kw):
        iface.emit("cmd")
        return {"type": "cmd"}
    def _handle_res(res=None, props={}, **kw):
        iface.emit("res", res, props)
        return {"type": "res", "res": res, "props": props}
    def _handle_signal(name=None, value=None, props={}, **kw):
        if not (isinstance(name, str) and name.isidentifier()):
            return
        props = std_arg({}, props)
        iface.emit("signal::%s" % name.replace('_', '-'),
                   name, value, props)
        return {"type": "res", "name": name, "value": value, "props": props}
    attr_table = {
        "config": new_wrapper2(get_config, None),
        "start": send_start,
        "prop": new_wrapper(send_prop, None) if sync else send_prop,
        "cmd": new_wrapper(lambda name:
                           (lambda *args, **kwargs:
                            send_cmd(name, *args, **kwargs))),
        "lock": send_lock,
        "quit": send_quit,
        "alarm": new_wrapper(lambda name:
                             (lambda nid, **args:
                              send_alarm(name, nid, **args)))
    }
    class PythonSlave(GObject.Object):
        __gsignals__ = {
            "config": (GObject.SignalFlags.RUN_FIRST,
                       GObject.TYPE_NONE,
                       (GObject.TYPE_STRING, GObject.TYPE_STRING,
                        GObject.TYPE_PYOBJECT)),
            "quit": (GObject.SignalFlags.RUN_FIRST,
                     GObject.TYPE_NONE,
                     ()),
            "ready": (GObject.SignalFlags.RUN_FIRST,
                      GObject.TYPE_NONE,
                      ()),
            "cmd": (GObject.SignalFlags.RUN_FIRST,
                    GObject.TYPE_NONE,
                    ()),
            "res": (GObject.SignalFlags.RUN_FIRST,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
            "alarm": (GObject.SignalFlags.RUN_FIRST |
                      GObject.SignalFlags.DETAILED,
                      GObject.TYPE_NONE,
                      (GObject.TYPE_STRING, GObject.TYPE_STRING,
                       GObject.TYPE_PYOBJECT)),
            "error": (GObject.SignalFlags.RUN_FIRST,
                      GObject.TYPE_NONE,
                      (GObject.TYPE_INT, GObject.TYPE_STRING)),
            "lock": (GObject.SignalFlags.RUN_FIRST,
                     GObject.TYPE_NONE,
                     (GObject.TYPE_BOOLEAN,)),
            "init": (GObject.SignalFlags.RUN_FIRST,
                     GObject.TYPE_NONE,
                     (GObject.TYPE_STRING,)),
            "alarm-success": (GObject.SignalFlags.RUN_FIRST |
                              GObject.SignalFlags.DETAILED,
                              GObject.TYPE_NONE,
                              (GObject.TYPE_STRING, GObject.TYPE_STRING,
                               GObject.TYPE_BOOLEAN)),
            "prop": (GObject.SignalFlags.RUN_FIRST,
                     GObject.TYPE_NONE,
                     (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
            "signal": (GObject.SignalFlags.RUN_FIRST |
                       GObject.SignalFlags.DETAILED,
                       GObject.TYPE_NONE,
                       (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT,
                        GObject.TYPE_PYOBJECT)),
        }
        def __init__(self):
            super().__init__()
        def do_quit(self):
            if sync:
                exit()
        def __getattr__(self, key):
            try:
                return attr_table[key]
            except KeyError:
                raise AttributeError(key)
    iface = PythonSlave()
    return iface

def main():
    fname = sys.argv[1]
    sys.argv.pop(0)
    sync = sys.argv.pop(0)
    if sync.lower() == 'false':
        sync = False
    else:
        sync = True
    conn = get_passed_conns(gtype=JSONSock)[0]
    iface = new_iface(conn, sync)

def start_slave(host, fname=None, args=[], sync=True, **kw):
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
    sync = str(bool(sync))
    conn = exec_n_conn(sys.executable,
                       args=[sys.executable, __file__, sync, fname] + args,
                       n=1, gtype=JSONSock)[0]
    return host.add_slave_from_jsonsock(self, sock)

if __name__ == '__main__':
    main()
elif 'setiface' in globals():
    setiface.slave.python = start_slave

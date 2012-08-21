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
import os
from os import path
import sys
import types
from srt_comm import *
from gi.repository import GObject, GLib
import time as _time

# requests: config, start, prop, cmd, lock, quit, alarm
# reply: error, alarm, lock, prop, init, ready, quit, config, cmd, res, signal


__all__ = ["InvalidRequest",
           "make_time",
           "new_iface",
           "default"]
default = None
sys.modules["%s.default" % __name__] = None
_slave_list = []

_plugins = SrtPlugins()

class SlaveLogger:
    def __init__(self):
        self._file = None
        self._fname = None
    def get_fname(self):
        return self._fname
    def set_fname(self, fname=None):
        if not self._file is None:
            self._file.close()
        if not isstr(fname):
            return
        fname = path.abspath(fname)
        dirname = path.dirname(fname)
        try:
            os.makedirs(dirname, 0o755, True)
        except:
            pass
        try:
            self._file = open(fname, 'a')
            self._fname = fname
        except:
            self._file = None
            self._fname = None
    def write(self, content):
        if self._file is None:
            return
        string = str(content)
        self._file.write('\n'.join([s for s in string.split('\n') if s]))
        self._file.write('\n')
        self._file.flush()
    def write_comment(self, content):
        if self._file is None:
            return
        string = str(content)
        self._file.write('# ')
        self._file.write('\n# '.join([s for s in string.split('\n') if s]))
        self._file.write('\n')
        self._file.flush()
    def __del__(self):
        self._file.close()

class InvalidRequest(Exception):
    pass

def make_time(tstr):
    try:
        return guess_time(tstr)
    except:
        pass
    return _time.time() + guess_interval(tstr)

def new_iface(conn, sync=True, as_default=True):
    _state = {"ready": False, "name": None}
    sync = bool(sync)
    logger = SlaveLogger()
    def disconn_cb(conn):
        iface.emit("quit")
    conn.connect("disconn", disconn_cb)
    conn.start_send()
    conn.start_recv()
    def got_obj_cb(conn, pkg):
        if pkg is None:
            iface.emit("quit")
            return
        try:
            pkg = __check_packages(**pkg)
        except:
            return
        if pkg is None:
            return
        __package_action(**pkg)
    conn.connect("got-obj", got_obj_cb)
    def _pong_back_cb():
        if not conn.send_buff_is_empty():
            send({"type": "pong"})
        return True
    GLib.timeout_add_seconds(10, _pong_back_cb)
    def send(obj):
        conn.send(obj)
        if sync:
            conn.wait_send()
    def send_start(name, args={}):
        iface.emit("log", "start", [name, args])
        send({"type": "start", "name": name, "args": args, "pwd": os.getcwd()})
    def send_float(float=True):
        float = bool(float)
        iface.emit("log", "float", float)
        send({"type": "float", "float": float})
    def send_prop(name):
        send({"type": "prop", "name": name})
        if not sync:
            return
        pkg = wait_with_cb(lambda pkg: (pkg["type"] == "error" or
                                        (pkg["type"] == "prop" and
                                         pkg["name"] == name)))
        if pkg["type"] == "error":
            raise InvalidRequest
        return pkg["value"]
    def send_query(name):
        send({"type": "query", "name": name})
        if not sync:
            return
        pkg = wait_with_cb(lambda pkg: (pkg["type"] == "error" or
                                        (pkg["type"] == "query" and
                                         pkg["name"] == name)))
        if pkg["type"] == "error":
            raise InvalidRequest
        return pkg["name_list"]
    def send_cmd(_name, *args, **kwargs):
        iface.emit("log", "cmd", [_name, args, kwargs])
        send({"type": "cmd", "name": _name, "args": args, "kwargs": kwargs})
        if not sync:
            return
        wait_types("cmd")
        pkg = wait_types(["error", "res"])
        if pkg["type"] == "error":
            raise InvalidRequest
        return pkg["res"], pkg["props"]
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
        iface.emit("log", "quit", "")
        send({"type": "quit"})
        iface.emit("quit")
    def send_slave_error(name=None, msg=None):
        send({"type": "slave-error", "name": name, "msg": msg})
    def send_alarm(_name, nid="", **args):
        send({"type": "alarm", "name": _name, "nid": nid, "args": args})
        if not sync:
            return
        pkg = wait_with_cb(lambda pkg: (pkg["type"] == "alarm" and
                                        pkg["name"] == _name and
                                        pkg["nid"] == nid and
                                        "success" in pkg))
        if pkg["success"]:
            return True
        raise InvalidRequest

    # config
    _config_cache = {}
    def _cache_config(field, name, value):
        set_2_level(_config_cache, field, name, value)
    def set_config(field, name, value):
        iface.emit("log", "set_config", [field, name, value])
        send({"type": "config", "field": field, "name": name,
              "set_value": True, "value": value})
        pkg = wait_with_cb(lambda pkg: (pkg["type"] == "config" and
                                        "set_value" in pkg and
                                        pkg["field"] == field and
                                        pkg["name"] == name))
        if pkg["success"]:
            return
        raise InvalidRequest
    def get_config(field, name, notify=True, non_null=False):
        try:
            return _config_cache[field][name]
        except:
            pass
        send({"type": "config", "field": field, "name": name,
              "notify": bool(notify)})
        if not sync:
            return
        pkg = wait_with_cb(lambda pkg: (pkg["type"] == "config" and
                                        (not "set_value" in pkg) and
                                        pkg["field"] == field and
                                        pkg["name"] == name))
        value = pkg["value"]
        if value is None and non_null:
            raise KeyError("config %s.%s not found" % (field, name))
        return pkg["value"]

    def __check_packages(type=None, **pkg):
        if type is None:
            return
        elif type == "ping":
            return {"type": "ping"}
        elif type == "quit":
            return {"type": "quit"}
        elif type == "ready":
            return {"type": "ready"}
        elif type == "config":
            return _check_config(**pkg)
        elif type == "prop":
            return _check_prop(**pkg)
        elif type == "query":
            return _check_query(**pkg)
        elif type == "alarm":
            return _check_alarm(**pkg)
        elif type == "error":
            return _check_error(**pkg)
        elif type == "lock":
            return _check_lock(**pkg)
        elif type == "init":
            return _check_init(**pkg)
        elif type == "cmd":
            return _check_cmd(**pkg)
        elif type == "res":
            return _check_res(**pkg)
        elif type == "signal":
            return _check_signal(**pkg)
    def __package_action(type=None, **pkg):
        if type == "quit":
            iface.emit("quit")
            return
        elif type == "ping":
            send({"type": "pong"})
            return
        elif type == "ready":
            _state["ready"] = True
            iface.emit("ready")
            return
        elif type == "config":
            return _config_action(**pkg)
        elif type == "prop":
            return _prop_action(**pkg)
        elif type == "query":
            return _query_action(**pkg)
        elif type == "alarm":
            return _alarm_action(**pkg)
        elif type == "error":
            return _error_action(**pkg)
        elif type == "lock":
            return _lock_action(**pkg)
        elif type == "init":
            return _init_action(**pkg)
        elif type == "cmd":
            return _cmd_action(**pkg)
        elif type == "res":
            return _res_action(**pkg)
        elif type == "signal":
            return _signal_action(**pkg)

    _wait_queue = []
    def _push_cb(cb, check_only):
        index = len(_wait_queue)
        obj = {"cb": cb, "check_only": check_only}
        _wait_queue.append(obj)
        return index
    def _push_package(index, pkg):
        if index >= len(_wait_queue):
            return
        _wait_queue[:] = _wait_queue[:index + 1]
        taken = False
        used = False
        for obj in _wait_queue:
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
        return used
    def _try_get_package(index):
        if index >= len(_wait_queue):
            return
        _wait_queue[:] = _wait_queue[:index + 1]
        if "res" in _wait_queue[-1]:
            return _wait_queue[-1]["res"]
        return
    def wait_with_cb(cb, check_only=False):
        if not hasattr(cb, '__call__'):
            raise TypeError("cb is not callable")
        check_only = bool(check_only)
        index = _push_cb(cb, check_only)
        while True:
            res = _try_get_package(index)
            if res:
                return res
            try:
                pkg = conn.recv()
            except GLib.GError:
                exit()
            if not pkg:
                exit()
            try:
                pkg = __check_packages(**pkg)
            except:
                continue
            if pkg is None:
                continue
            _push_package(index, pkg)
            __package_action(**pkg)
    def wait_types(types, check_only=False):
        if isstr(types):
            types = [types]
        return wait_with_cb(lambda pkg: (pkg["type"] in types), check_only)

    def _check_config(field=None, name=None, notify=False,
                      value=None, set_value=None, success=None, **kw):
        if not isstr(name) or not isstr(field) :
            return
        if set_value:
            return {"type": "config", "field": field, "name": name,
                    "set_value": True, "success": bool(success)}
        notify = bool(notify)
        return {"type": "config", "notify": notify,
                "field": field, "name": name, "value": value}
    def _check_prop(name=None, value=None, **kw):
        return {"type": "prop", "name": name, "value": value}
    def _check_query(name=None, name_list=None, **kw):
        return {"type": "query", "name": name, "name_list": name_list}
    def _check_alarm(name=None, nid=None, alarm=None,
                      success=None, **kw):
        if not isidentifier(name):
            return
        if not success is None:
            success = bool(success)
            return {"type": "alarm", "name": name, "nid": nid,
                    "success": success}
        return {"type": "alarm", "name": name, "nid": nid,
                "alarm": alarm}
    def _check_error(errno=None, msg=None, **kw):
        try:
            errno = int(errno)
        except:
            return
        msg = str(msg)
        return {"type": "error", "errno": errno, "msg": msg}
    def _check_lock(res=None, **kw):
        return {"type": "lock", "res": bool(res)}
    def _check_init(name=None, **kw):
        if not isstr(name):
            return
        return {"type": "init", "name": name}
    def _check_cmd(**kw):
        return {"type": "cmd"}
    def _check_res(res=None, name=None, props={}, args=[], kwargs={}, **kw):
        return {"type": "res", "res": res, "props": props, "name": name,
                "args": args, "kwargs": kwargs}
    def _check_signal(name=None, value=None, props={}, **kw):
        if not isidentifier(name):
            return
        props = std_arg({}, props)
        return {"type": "signal", "name": name,
                "value": value, "props": props}

    def _config_action(field=None, name=None, notify=False,
                       value=None, set_value=None, success=None, **kw):
        if set_value:
            return
        if notify:
            _cache_config(field, name, value)
        iface.emit("config", field, name, value)
    def _prop_action(name=None, value=None, **kw):
        iface.emit("prop", name, value)
    def _query_action(name=None, name_list=None, **kw):
        iface.emit("query::%s" % name.replace('_', '-'), name, name_list)
    def _alarm_action(name=None, nid=None, alarm=None,
                      success=None, **kw):
        if not success is None:
            iface.emit("alarm-success::%s" % name.replace('_', '-'),
                       name, nid, success)
            return
        iface.emit("alarm::%s" % name.replace('_', '-'),
                   name, nid, alarm)
    def _error_action(errno=None, msg=None, **kw):
        iface.emit("error", errno, msg)
        if sync:
            raise InvalidRequest
    def _lock_action(res=None, **kw):
        iface.emit("lock", res)
    def _init_action(name=None, **kw):
        _state["name"] = name
        iface.emit("init", name)
    def _cmd_action(**kw):
        iface.emit("cmd")
    def _res_action(res=None, name=None, props={}, args=[], kwargs={}, **kw):
        iface.emit("res::%s" % name.replace('_', '-'),
                   name, res, props, args, kwargs)
    def _signal_action(name=None, value=None, props={}, **kw):
        iface.emit("signal::%s" % name.replace('_', '-'),
                   name, value, props)

    def wait_ready():
        if _state["ready"]:
            return
        wait_types("ready")
    def get_name():
        return _state["name"]
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
            "res": (GObject.SignalFlags.RUN_FIRST |
                    GObject.SignalFlags.DETAILED,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_STRING,
                     GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,
                     GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
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
            "query": (GObject.SignalFlags.RUN_FIRST |
                      GObject.SignalFlags.DETAILED,
                      GObject.TYPE_NONE,
                      (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
            "signal": (GObject.SignalFlags.RUN_FIRST |
                       GObject.SignalFlags.DETAILED,
                       GObject.TYPE_NONE,
                       (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT,
                        GObject.TYPE_PYOBJECT)),
            "log": (GObject.SignalFlags.RUN_FIRST |
                    GObject.SignalFlags.DETAILED,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
        }
        def __init__(self):
            super(PythonSlave, self).__init__()
        def do_quit(self):
            if sync:
                exit()
        def do_init(self, name):
            if "logger" in _state:
                return
            try:
                _state["logger"] = _plugins.logger[name](self, logger)
            except:
                print_except()
    iface = PythonSlave()
    module_dict = {
        "record": logger.set_fname,
        "float": send_float,
        "write_log": logger.write,
        "wait_ready": wait_ready,
        "get_name": get_name,
        "make_time": make_time,
        "time_passed": lambda t: _time.time() >= t,
        "config": new_wrapper2(get_config, None),
        "set_config": set_config,
        "start": send_start,
        "prop": new_wrapper(send_prop, None) if sync else send_prop,
        "query": new_wrapper(send_query, None) if sync else send_query,
        "cmd": new_wrapper(lambda name:
                           (lambda *args, **kwargs:
                            send_cmd(name, *args, **kwargs)), None),
        "lock": lambda wait=True: send_lock(True, wait=wait),
        "unlock": lambda: send_lock(False),
        "quit": send_quit,
        "slave_error": send_slave_error,
        "alarm": new_wrapper(lambda name:
                             (lambda nid, **args:
                              send_alarm(name, nid, **args)), None),
        "slave": iface,
        "logger": logger,
        "InvalidRequest": InvalidRequest
    }
    module = _add_module(module_dict, as_default)
    return module

def _add_module(module_dict, as_default):
    self = sys.modules[__name__]
    name = "srt_slave%d" % len(_slave_list)
    module = types.ModuleType(name, self.__doc__)
    module.__dict__.update(module_dict)
    _slave_list.append(module)
    self.__dict__[name] = module
    sys.modules["%s.%s" % (__name__, name)] = module
    if as_default:
        self.default = module
        sys.modules["%s.default" % __name__] = module
    return module

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
from srt_comm import config as glob_conf
from gi.repository import GObject, GLib
from srt_client.srtconf import *
from srt_client.srtremote import *
from srt_client.srthost import *
import sys

class SrtCenter(GObject.Object):
    __gsignals__ = {
        "init": (GObject.SignalFlags.RUN_FIRST,
                 GObject.TYPE_NONE,
                 (GObject.TYPE_STRING,)),
        "ready": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  ()),
        "quit": (GObject.SignalFlags.RUN_FIRST,
                 GObject.TYPE_NONE,
                 ()),
        "error": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_INT, GObject.TYPE_STRING)),
    }
    def __init__(self, config={}):
        super(SrtCenter, self).__init__()
        self._mainloop = GLib.MainLoop()
        self._remote_err_id = 0
        self._plugins = SrtPlugins()
        self.__init_config__(config)
        self.__init_remote__()
        self.__init_helper__()
        self.__init_host__()

    def __init_host__(self):
        self._host = SrtHost(self._plugins)
        self._host.connect("prop", self._host_prop_cb)
        self._host.connect("query", self._host_query_cb)
        self._host.connect("cmd", self._host_cmd_cb)
        self._host.connect("config", self._host_config_cb)
        self._host.connect("set-config", self._host_set_config_cb)
        self._host.connect("quit", self._host_quit_cb)

    def __init_config__(self, config):
        self._config = SrtConf()
        try:
            for field, group in config.items():
                try:
                    for key, value in group.items():
                        try:
                            self._config[field][key] = value
                        except:
                            print_except()
                except:
                    print_except()
        except:
            pass
        self._config_notify = {}
        self._config.connect("updated", self._config_updated_cb)
    def _config_updated_cb(self, config, field, name):
        try:
            cbargs = self._config_notify[field][name]
        except:
            return
        value = self._config._get_config(field, name)
        cbargs[:] = [[cb, args] for [cb, args] in cbargs
                     if call_catch(cb, field, name, value, *args)]
    def __init_remote__(self):
        if self._remote_err_id:
            self._remote.disconnect(self._remote_err_id)
            self._remote.close()
        self._remote = SrtRemote(self._plugins)
        self._remote_err_id = self._remote.connect('error', self._remote_err_cb)
        self._remote.connect('initialized', self._remote_init_cb)
        self._remote.connect('ready', self._remote_ready_cb)
        self._remote.connect('got-obj', self._remote_got_obj_cb)
        self._remote.connect('reconnect', self._remote_reconnect_cb)
    def __init_helper__(self):
        self._helper = exec_n_conn(sys.executable,
                                   args=[sys.executable, glob_conf.SRT_HELPER],
                                   n=1, gtype=JSONSock)[0]
        self._helper.start_send()
        self._helper.start_recv()
        self._helper.connect('disconn', self._helper_disconn_cb)
        self._helper.connect('got-obj', self._helper_got_obj_cb)
        self._helper_alarm = {}
    def _host_prop_cb(self, host, sid, name):
        self._helper.send({"type": "prop", "sid": sid, "name": name})
    def _host_query_cb(self, host, sid, name):
        self._helper.send({"type": "query", "sid": sid, "name": name})
    def _host_cmd_cb(self, host, sid, name, args, kwargs):
        try:
            args = list(args)
        except:
            args = []
        try:
            kwargs = dict(kwargs)
        except:
            kwargs = {}
        self._helper.send({"type": "slave", "sid": sid, "name": name,
                           "args": args, "kwargs": kwargs})
    def _host_quit_cb(self, host):
        self._quit()
    def _host_config_cb(self, host, sid, field, name, notify):
        value = self._get_config(field, name, notify,
                                 self._host_config_notify_cb, sid)
        self._host.feed_config(sid, field, name, value, notify)
    def _host_set_config_cb(self, host, field, name, value):
        try:
            self._config[field][name] = value
        except:
            print_except()
    def _host_config_notify_cb(self, field, name, value, sid):
        return self._host.feed_config(sid, field, name, value, True)

    def _helper_got_obj_cb(self, helper, pkg):
        pkgtype = get_dict_fields(pkg, "type")
        if pkgtype is None:
            return
        if pkgtype == "remote":
            self._helper_handle_remote(**pkg)
            return
        elif pkgtype == "slave":
            self._helper_handle_slave(**pkg)
            return
        elif pkgtype == "ready":
            self.emit('ready')
            return
        elif pkgtype == "got-cmd":
            self._helper_handle_got_cmd(**pkg)
            return
        elif pkgtype == "quit":
            self._quit()
            return
        elif pkgtype == "config":
            self._helper_handle_config(**pkg)
            return
        elif pkgtype == "prop":
            self._helper_handle_prop(**pkg)
            return
        elif pkgtype == "query":
            self._helper_handle_query(**pkg)
            return
        elif pkgtype == "signal":
            self._helper_handle_signal(**pkg)
            return
        elif pkgtype == "alarm":
            self._helper_handle_alarm(**pkg)
            return
        return
    def _helper_handle_alarm(self, name="", nid=None, args={}, **kw):
        if (not (isidentifier(name) and isinstance(args, dict))
            or isinstance(nid, list) or isinstance(nid, dict)):
            self._helper.send({"type": "alarm", "name": name, "nid": nid,
                               "success": False})
            return
        if not name in self._helper_alarm:
            self._helper_alarm[name] = {}
        try:
            alarm = self._plugins.alarm[name](**args)
            alarm.connect("alarm", self._helper_alarm_cb, name, nid)
        except Exception as err:
            print_except()
            self._helper.send({"type": "alarm", "name": name, "nid": nid,
                               "success": False})
            return
        self._helper.send({"type": "alarm", "name": name, "nid": nid,
                           "success": True})
        try:
            self._helper_alarm[name][nid].stop()
        except:
            pass
        self._helper_alarm[name][nid] = alarm
    def _helper_alarm_cb(self, obj, alarm, name, nid):
        self._helper.send({"type": "alarm", "name": name,
                           "nid": nid, "alarm": alarm})

    def _helper_handle_signal(self, name=None, value=None, props={}, **kw):
        if not isidentifier(name):
            return
        self._host.feed_signal(name, value, props)
    def _helper_handle_prop(self, sid=None, name=None, value=None, **kw):
        if None in [name, value]:
            return
        self._host.feed_prop(sid, name, value)
    def _helper_handle_query(self, sid=None, name=None, name_list=None, **kw):
        if None in [name, name_list]:
            return
        self._host.feed_query(sid, name, name_list)
    def _helper_handle_got_cmd(self, sid=None, **kw):
        self._host.feed_got_cmd(sid)
    def _helper_handle_slave(self, sid=None, obj=None, **kw):
        if obj is None:
            return
        self._host.feed_res(sid, obj)
    def _helper_handle_config(self, field=None, name=None, notify=False,
                              set_value=None, value=None, **kw):
        if not isstr(field) or not isstr(name):
            return
        if set_value:
            try:
                self._config[field][name] = value
            except:
                print_except()
            return
        notify = bool(notify)
        value = self._get_config(field, name, notify,
                                 self._helper_config_notify_cb)
        self._helper.send({"type": "config", "field": field, "name": name,
                           "value": value, "notify": notify})

    def _helper_handle_remote(self, obj=None, **kw):
        if obj is None:
            return
        objtype = get_dict_fields(obj, "type")
        if objtype == "quit":
            self._quit()
            return
        self._remote.request(obj)
    def _helper_config_notify_cb(self, field, name, value):
        self._helper.send({"type": "config", "field": field, "name": name,
                           "value": value, "notify": True})
        return True
    def _helper_disconn_cb(self, helper):
        self.emit('error', SRTERR_HELPER_QUIT, "Helper quit")
        self._quit()

    def _remote_err_cb(self, remote, errno, msg):
        self.emit('error', errno, msg)
        if errno in [SRTERR_CONN, SRTERR_BUSY, SRTERR_PLUGIN]:
            self._quit()
    def _remote_init_cb(self, remote, name):
        self._helper.send({"type": "init", "name": name})
        self.emit('init', name)
    def _remote_ready_cb(self, remote):
        self._helper.send({"type": "ready"})
    def _remote_got_obj_cb(self, remote, obj):
        self._helper.send({"type": "remote", "obj": obj})
    def _remote_reconnect_cb(self, remote):
        self.__init_remote__()
        self._start_remote()
    def _quit(self):
        self.emit('quit')
        self._mainloop.quit()
    def do_quit(self):
        self._remote.request({"type": "quit"})
        try:
            self._remote.wait_send()
            self._remote.close()
        except GLib.GError:
            pass
        self._host.quit()
        self._helper.send({"type": "quit"})
        try:
            self._helper.wait_send()
        except GLib.GError:
            pass
    def do_error(self, errno, msg):
        self._helper.send({"type": "error", "errno": errno, "msg": msg})
    def do_init(self, name):
        self._host.init(name)
    def do_ready(self):
        self._host.ready()
    def create_slave_by_name(self, name, pwd, args):
        return self._host.create_slave_by_name(name, pwd, args)
    def add_slave_from_jsonsock(self, sock):
        return self._host.add_slave_from_jsonsock(sock)
    def run(self):
        self._start_remote()
        try:
            self._mainloop.run()
        except:
            self._quit()
    def _get_config(self, field, name, notify, cb, *args):
        value = self._config._get_config(field, name)
        if not notify:
            return value
        if not field in self._config_notify:
            self._config_notify[field] = {}
        if not name in self._config_notify[field]:
            self._config_notify[field][name] = []
        self._config_notify[field][name].append([cb, args])
        return value
    def _start_remote(self):
        host = str(self._config.generic.host)
        port = int(self._config.generic.port)
        init = None
        try:
            init = str(self._config.generic.initializer)
        except:
            pass
        if init is None:
            self._remote.init((host, port))
        else:
            self._remote.init((host, port), init=init)

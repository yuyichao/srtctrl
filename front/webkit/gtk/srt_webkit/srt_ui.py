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

from gi.repository import WebKit, Gtk, GLib, GObject
from .util import *
from .view import SrtView
# from .inspector import SrtInspector
from srt_comm import *
import srt_comm
import json
import os

class SrtUI:
    def __init__(self, uri, conn):
        self._ref = 0
        self._refresh_wait_to = 0
        self._new_view = None
        self._new_alert = 0
        self._ready = False
        self._view = SrtView()
        self._view.set_hexpand(True)
        self._view.set_vexpand(True)
        self._grid = Gtk.Table()
        self._grid.set_hexpand(True)
        self._grid.set_vexpand(True)
        self._grid.attach(self._view, 0, 1, 0, 1,
                          Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND |
                          Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.FILL |
                          Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.SHRINK,
                          0, 0)
        self._window = Gtk.Window()
        self._window.set_default_size(500, 400)
        self._window.add(self._grid)
        self._window.connect("destroy", self._win_close_cb)
        self._view_alert = self._view.connect("script-alert",
                                              self._script_alert_cb)
        self._uri = uri
        self._view.load_uri(uri)
        self._conn = conn
        self._name = None
        # self._inspector = None
        self._conn.connect('disconn', self._disconn_cb)
        GLib.timeout_add_seconds(10, self._pong_back_cb)
        GLib.timeout_add_seconds(600, self._do_refresh)
        self.__init_conn__()
        self._pkg_timeout = 0
        self._pkg_queue = []
        self._srt_state = {}
    def _pong_back_cb(self):
        if not self._conn.send_buff_is_empty():
            self._conn.send({"type": "pong"})
        return True
    def __init_conn__(self):
        self._conn.start_send()
        self._conn.start_recv()
        self._conn.connect("got-obj", self._got_obj_cb)
    def _disconn_cb(self, conn):
        self._got_obj_cb(conn, {'type': 'quit'})
    def _got_obj_cb(self, conn, pkg):
        try:
            pkgtype = pkg['type']
        except:
            return
        if pkg['type'] == 'init':
            try:
                self._name = pkg['name']
            except:
                pass
            if not self._name:
                pkg = {'type': 'quit'}
        if not self._pkg_timeout:
            self._pkg_timeout = GLib.timeout_add(50, self._push_pkgs_cb)
        self._pkg_queue.append(pkg)
    def _push_pkgs_cb(self):
        if not self._ready:
            return True
        self._pkg_timeout = 0
        pkgs = self._pkg_queue
        self._pkg_queue = []
        self._view.execute_script('try{SrtGotPkgs(%s)}catch(e){}' %
                                  json.dumps(pkgs))
        return False
    def _win_close_cb(self, win):
        Gtk.main_quit()
    def show_all(self):
        self._window.show_all()
    # def show_inspector(self):
    #     self._view.get_settings().set_property("enable-developer-extras", True)
    #     inspector = self._view.get_inspector()
    #     if self._inspector is None:
    #         self._inspector = SrtInspector(inspector)
    #     inspector.show()
    #     self._inspector.connect('destroy', self._inspector_destroy_cb)
    # def _inspector_destroy_cb(self, inspector):
    #     self.hide_inspector()
    # def hide_inspector(self):
    #     self._view.get_settings().set_property("enable-developer-extras",
    #                                            False)
    #     if not self._inspector is None:
    #         inspector = self._inspector
    #         self._inspector = None
    #         inspector.destroy()
    def _script_alert_cb(self, view, frame, msg):
        try:
            call = json.loads(msg)
        except:
            return False
        if not isinstance(call, dict):
            return False
        self.__srt_call(view, **call)
        return True
    def __srt_call(self, view, type=None, ret_var=None, args=None, **kw):
        if type is None or not isstr(type):
            return
        try:
            res = self.__handle_calls(view, type, args)
            view.execute_script("%s = {res: %s};" %
                                (ret_var, json.dumps(res)))
        except:
            # print_except()
            pass
    def __handle_calls(self, view, type, args):
        if type == 'open':
            return self._handle_open(view, args)
        elif type == 'file':
            return self._handle_file(view, args)
        elif type == 'quit':
            return Gtk.main_quit()
        elif type == 'send':
            return self._handle_send(view, args)
        elif type == 'os':
            return self._handle_os(view, args)
        elif type == 'name':
            return self._handle_name(view, args)
        elif type == 'srt':
            return self._handle_srt(view, args)
        elif type == 'dev':
            return self._handle_dev(view, args)
        elif type == 'state':
            return self._handle_state(view, args)
        elif type == 'refresh':
            return self._handle_refresh(view, args)
        elif type == 'ready':
            return self._handle_ready(view, args)
        elif type == 'ref':
            return self._handle_ref(view, args)
    def _handle_open(self, view, uri):
        return openuri(uri)
    def _handle_file(self, view, kw):
        return file_dialog(**kw)
    def _handle_send(self, view, pkg):
        self._conn.send(pkg)
    def _handle_os(self, view, args):
        name = args[0]
        args = args[1:]
        return getattr(os, name)(*args)
    def _handle_name(self, view, args):
        c = GLib.main_context_default()
        while not self._name:
            c.iteration(True)
        return self._name
    def _handle_srt(self, view, args):
        name = args[0]
        args = args[1:]
        return getattr(srt_comm, name)(*args)
    def _handle_ref(self, view, args):
        self._ref += args
    def _handle_ready(self, view, args):
        self._ready = True
        if self._new_view is None:
            return
        self._grid.attach(self._new_view, 0, 1, 0, 1,
                          Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND |
                          Gtk.AttachOptions.SHRINK, Gtk.AttachOptions.FILL |
                          Gtk.AttachOptions.EXPAND | Gtk.AttachOptions.SHRINK,
                          0, 0)
        self._grid.remove(self._view)
        self._view.disconnect(self._view_alert)
        self._view = self._new_view
        self._view_alert = self._new_alert
        self._new_view = None
        self._new_alert = 0
        self._ref = 0
    def _handle_refresh(self, view, args):
        if not self._new_view is None:
            return
        self._do_refresh()
        raise Exception
    def _refresh_to_cb(self):
        if self._ref > 0:
            return True
        self._refresh_wait_to = 0
        self._real_refresh()
        return False
    def _do_refresh(self):
        if self._ref > 0:
            if self._refresh_wait_to:
                return
            self._refresh_wait_to = GLib.timeout_add(
                500, self._refresh_to_cb)
            return
        self._real_refresh()
    def _real_refresh(self):
        new_view = SrtView()
        new_view.show()
        new_view.set_hexpand(True)
        new_view.set_vexpand(True)
        self._new_view = new_view
        self._new_alert = new_view.connect("script-alert",
                                           self._script_alert_cb)
        new_view.load_uri(self._uri)
    # def _handle_dev(self, args):
    #     return self.show_inspector()
    def _handle_state(self, view, args):
        key = args[0]
        try:
            value = args[1]
            self._srt_state[key] = value
            return
        except:
            pass
        try:
            return self._srt_state[key]
        except:
            pass

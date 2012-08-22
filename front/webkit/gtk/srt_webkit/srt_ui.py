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
from .inspector import SrtInspector
from srt_comm import *
import srt_comm
import json
import os

class SrtUI:
    def __init__(self, uri, conn):
        self._view = SrtView()
        self._window = Gtk.Window()
        self._window.set_default_size(500, 400)
        self._window.add(self._view)
        self._window.connect("destroy", self._win_close_cb)
        self._view.connect("load-finished", self._load_finish_cb)
        self._view.connect("script-alert", self._script_alert_cb)
        self._view.load_uri(uri)
        self._conn = conn
        self._name = None
        self._conn.connect('disconn', self._disconn_cb)
        GLib.timeout_add_seconds(10, self._pong_back_cb)
        self.__init_conn__()
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
        self._view.execute_script('SrtGotObj(%s)' %
                                  json.dumps(pkg))
    def _load_finish_cb(self, view, frame):
        pass
    def _win_close_cb(self, win):
        Gtk.main_quit()
    def show_all(self):
        self._window.show_all()
    def show_inspector(self):
        self._view.get_settings().set_property("enable-developer-extras",True)
        inspector = self._view.get_inspector()
        if self._inspector is None:
            self._inspector = SrtInspector(inspector)
        inspector.show()
    def _script_alert_cb(self, view, frame, msg):
        try:
            return self.__srt_call(**json.loads(msg))
        except:
            print_except()
            return False
    def __srt_call(self, type=None, callback=None, args=None):
        res = None
        if type == None:
            return False
        elif type == 'open':
            res = self._handle_open(args)
        elif type == 'file':
            res = self._handle_file(args)
        elif type == 'quit':
            Gtk.main_quit()
        elif type == 'send':
            res = self._handle_send(args)
        elif type == 'os':
            res = self._handle_os(args)
        elif type == 'name':
            res = self._handle_name(args)
        elif type == 'srt':
            res = self._handle_srt(args)
        self._view.execute_script("%s(%s)" % (callback, json.dumps(res)))
        return True
    def _handle_open(self, uri):
        return openuri(uri)
    def _handle_file(self, kw):
        return file_dialog(**kw)
    def _handle_send(self, pkg):
        self._conn.send(pkg)
    def _handle_os(self, args):
        name = args[0]
        args = args[1:]
        return getattr(os, name)(*args)
    def _handle_name(self, args):
        c = GLib.main_context_default()
        while not self._name:
            c.iteration(True)
        return self._name
    def _handle_srt(args):
        name = args[0]
        args = args[1:]
        return getattr(srt_comm, name)(*args)

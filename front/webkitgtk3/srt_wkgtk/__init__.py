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
from pywkjs import *

from gi.repository import WebKit, Gtk, GLib, GObject
from .window import SrtWindow
from .inspector import SrtInspector
import srt_comm

def openuri(uri, *args):
    import subprocess
    browser = 'xdg-open'
    subprocess.Popen([browser, uri])

class Obj(object):
    pass

def js_call_py(func, args, kwargs):
    try:
        args = list(args)
    except:
        args = []
    try:
        kwargs = dict((key, kwargs[key]) for key in kwargs)
    except:
        kwargs = {}
    return func(*args, **kwargs)

class SrtUI:
    def __init__(self, uri, exp_dict):
        self._window = SrtWindow()
        self._window.window.connect("destroy", self._win_close_cb)
        self._window.helper.connect("window-object-cleared", self._win_clr_cb)
        self._window.webview.connect("load-finished", self._load_finish_cb)
        self._window.webview.connect("console-message", self._console_log_cb)
        self._window.load_uri(uri)
        self._inspector = None
        self._exp_dict = exp_dict
    def _win_clr_cb(self, helper, frame, winobj):
        winobj.UI = Obj()
        winobj.UI.Gtk = Gtk
        winobj.UI.GLib = GLib
        winobj.UI.GObject = GObject
        winobj.UI.WebKit = WebKit
        winobj.UI.window = self._window.window
        winobj.UI.webview = self._window.webview
        winobj.UI.show_inspector = self.show_inspector
        winobj.Back = self._exp_dict
        winobj.SrtUtil = srt_comm
        winobj.SrtState = {}
        winobj.PyUtil = {
            "call": js_call_py
        }
        winobj.open = openuri
    def _load_finish_cb(self, view, frame):
        pass
    def _win_close_cb(self, win):
        Gtk.main_quit()
    def _console_log_cb(self, view, msg, line, src):
        return False
    def show_all(self):
        self._window.show_all()
    def show_inspector(self):
        view = self._window.webview
        view.get_settings().set_property("enable-developer-extras",True)
        inspector = self._window.webview.get_inspector()
        if self._inspector is None:
            self._inspector = SrtInspector(inspector)
        inspector.show()

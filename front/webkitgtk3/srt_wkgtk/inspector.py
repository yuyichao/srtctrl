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

from gi.repository import WebKit, Gtk
from .window import SrtWindow
import srt_comm

class SrtInspector ():
    def __init__ (self, inspector):
        self.webview = WebKit.WebView()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self.webview)
        scrolled_window.show_all()

        self.window = Gtk.Window()
        self.window.add(scrolled_window)
        self.window.set_default_size(500, 400)
        self.window.set_title("Srt Inspector")
        self.window.connect("delete-event", self.on_delete_event)

        inspector.set_property("javascript-profiling-enabled", True)
        inspector.connect("inspect-web-view", self.on_inspect_web_view)
        inspector.connect("show-window", self.on_show_window)
        inspector.connect("close-window", self.on_close_window)
        inspector.connect("finished", self.on_finished)

    def __del__ (self):
        self.window.destory()

    def on_delete_event (self, widget, event):
        self.window.hide()
        return True

    def on_inspect_web_view (self, inspector, web_view):
        return self.webview

    def on_show_window (self, inspector):
        self.window.present()
        return True

    def on_close_window (self, inspector):
        self.window.hide()
        return True

    def on_finished (self, inspector):
        self.window.hide()

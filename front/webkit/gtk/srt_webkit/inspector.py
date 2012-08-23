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

from gi.repository import WebKit, Gtk
import srt_comm

class SrtInspector(Gtk.Window):
    def __init__(self, inspector):
        super(SrtInspector, self).__init__()
        self._view = WebKit.WebView()

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.add(self._view)
        scrolled_window.show_all()

        self.add(scrolled_window)
        self.set_default_size(500, 400)
        self.set_title("Srt Inspector")

        self._inspector = inspector
        inspector.set_property("javascript-profiling-enabled", True)
        inspector.connect("inspect-web-view", self._inspect_web_view_cb)
        inspector.connect("show-window", self._show_window_cb)
        inspector.connect("close-window", self._close_window_cb)
        inspector.connect("finished", self._finished_cb)
        self.connect('delete-event', self._delete_cb)

    def _delete_cb(self, win, event):
        self.hide()
        return True
    def _inspect_web_view_cb(self, inspector, web_view):
        return self._view
    def _show_window_cb(self, inspector):
        self.present()
        return True
    def _close_window_cb(self, inspector):
        self.hide()
        return True
    def _finished_cb(self, inspector):
        self.hide()

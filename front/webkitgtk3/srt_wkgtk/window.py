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
from pywkjs import *

class SrtWindow:
    def __init__(self):
        self.window = Gtk.Window()
        self.window.set_default_size(500, 400)
        self.webview = WebKit.WebView()
        self.webview.connect("new-window-policy-decision-requested",
                             self._new_window_requested)
        self.window.add(self.webview)
        self.helper = Helper(self.webview)
        settings = self.webview.get_settings()
        settings.set_property('enable-universal-access-from-file-uris', True)
        settings.set_property('enable-file-access-from-file-uris', True)
        settings.set_property('javascript-can-access-clipboard', True)
        settings.set_property('enable-default-context-menu', True)
        settings.set_property('enable-page-cache', True)
        settings.set_property('tab-key-cycles-through-elements', True)
        settings.set_property('enable-spell-checking', False)
        settings.set_property('enable-caret-browsing', False)
    def _new_window_requested(self, view, frame, request, action, decision):
        decision.ignore()
        uri = request.get_uri()
        import subprocess
        browser = 'xdg-open'
        subprocess.Popen([browser, uri])
        return True
    def show_all(self):
        self.window.show_all()
    def load_uri(self, uri):
        self.webview.load_uri(uri)

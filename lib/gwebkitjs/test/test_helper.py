#!/usr/bin/env python

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

from gi.repository import Gtk, GWebKitJS, WebKit, GLib
import os, sys

def win_obj_clr_cb(helper, frame, ctx, obj):
    print(helper.get_view(), frame, ctx, obj)
    ctx.set_property(obj, "pyobj", ctx.make_string("this is a py str"), 0)

def load_finished_cb(view, frame):
    Gtk.main_quit()

Gtk.init([])

win = Gtk.Window()
webview = WebKit.WebView()
win.add(webview)
win.show_all()
win.connect("destroy", Gtk.main_quit)

path = sys.argv[1]
url = GLib.filename_to_uri(path, None)

helper = GWebKitJS.Helper.new(webview)
helper.connect("window-object-cleared", win_obj_clr_cb)
webview.load_uri(url)
webview.connect("load-finished", load_finished_cb)

Gtk.main()

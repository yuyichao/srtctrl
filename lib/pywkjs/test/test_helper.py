#!/usr/bin/env python

from gi.repository import Gtk, WebKit, GLib
from pywkjs import *
import os, sys

def win_obj_clr_cb(helper, frame, obj):
    print(helper.get_view(), frame, obj)
    obj.pyobj = "this is a py str"

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

helper = Helper(webview)
helper.connect("window-object-cleared", win_obj_clr_cb)
webview.load_uri(url)
webview.connect("load-finished", load_finished_cb)

Gtk.main()

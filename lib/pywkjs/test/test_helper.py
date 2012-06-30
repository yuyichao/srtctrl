#!/usr/bin/env python

from gi.repository import Gtk, WebKit, GLib
from pywkjs import *
import os, sys

def printr():
    _print = print
    def printr(*arg, **kwarg):
        end = '\n'
        if 'end' in kwarg:
            end = kwarg['end']
        kwarg['end'] = ''
        _print('\033[31;1m', end='')
        _print(*arg, **kwarg)
        _print('\033[0m', end=end)
    return printr
printr = printr()

def _print():
    _print = print
    def __print(*arg, **kwarg):
        end = '\n'
        if 'end' in kwarg:
            end = kwarg['end']
        kwarg['end'] = ''
        _print('\033[32;1m', end='')
        _print(*arg, **kwarg)
        _print('\033[0m', end=end)
    return __print
print = _print()

printr('\nTest Start')

def win_obj_clr_cb(helper, frame, obj):
    obj.pyobj = "this is a py str"
    obj.button = button
    globals()['jseval'] = obj.eval

def load_finished_cb(view, frame):
    print(jseval)
    print(jseval("[1, 2, 3, 4]"))
    print(jseval("function a(){return 5;}; a"))
    func = jseval("function a() {return 5;}; a");
    print(func())
    print(jseval("null"))
    print(jseval("a = {}"))

def console_log(view, msg, line, src):
    print("%s\n@#%d: %s" % (src, line, msg))
    return True

Gtk.init([])

win = Gtk.Window()
vbox = Gtk.VBox()
webview = WebKit.WebView()
button = Gtk.Button("aaaa")
vbox.add(webview)
vbox.add(button)
win.add(vbox)
win.show_all()
win.connect("destroy", Gtk.main_quit)

path = sys.argv[1]
url = GLib.filename_to_uri(path, None)

helper = Helper(webview)
helper.connect("window-object-cleared", win_obj_clr_cb)
webview.load_uri(url)
webview.connect("load-finished", load_finished_cb)
webview.connect("console-message", console_log)

Gtk.main()

printr('Test End\n')

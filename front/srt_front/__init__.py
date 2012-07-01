from pywkjs import *

from gi.repository import WebKit, Gtk
from srt_front.window import SrtWindow

class Obj(object):
    pass

class SrtUI:
    def __init__(self, uri, exp_dict):
        self._window = SrtWindow()
        self._window.window.connect("destroy", self._win_close_cb)
        self._window.helper.connect("window-object-cleared", self._win_clr_cb)
        self._window.webview.connect("load-finished", self._load_finish_cb)
        self._window.webview.connect("console-message", self._console_log_cb)
        self._window.load_uri(uri)
        self._exp_dict = exp_dict
    def _win_clr_cb(self, helper, frame, winobj):
        self._winobj = winobj
        winobj.UI = Obj()
        winobj.UI.Gtk = Gtk
        winobj.UI.WebKit = WebKit
        winobj.UI.window = self._window.window
        winobj.UI.webview = self._window.webview
        winobj.Back = self._exp_dict
    def _load_finish_cb(self, view, frame):
        pass
    def _win_close_cb(self, win):
        Gtk.main_quit()
    def _console_log_cb(self, view, msg, line, src):
        return False
    def show_all(self):
        self._window.show_all()

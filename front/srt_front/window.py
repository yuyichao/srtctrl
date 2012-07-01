from gi.repository import WebKit, Gtk
from pywkjs import *

class SrtWindow:
    def __init__(self):
        self.window = Gtk.Window()
        self.webview = WebKit.WebView()
        self.window.add(self.webview)
        self.helper = Helper(self.webview)
    def show_all(self):
        self.window.show_all()
    def load_uri(self, uri):
        self.webview.load_uri(uri)

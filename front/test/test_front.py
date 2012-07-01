import srt_front, sys
from gi.repository import GLib, Gtk, GObject

class FakeSource(GObject.Object):
    def __init__(self):
        pass

def main():
    path = sys.argv[1]
    uri = GLib.filename_to_uri(path, None)
    ui = srt_front.SrtUI(uri, {"a": [0, 1, 2, 3]})
    ui.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()

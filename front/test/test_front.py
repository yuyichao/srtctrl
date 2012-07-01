import srt_front, sys
from gi.repository import GLib, Gtk, GObject
import random

class FakeSource(GObject.Object):
    __gsignals__ = {
        "event": (GObject.SignalFlags.RUN_FIRST |
                  GObject.SignalFlags.DETAILED,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_PYOBJECT,))
    }
    def __init__(self):
        super().__init__()
        self._az = 0
        self._el = 0
        self._fake_events = [self.fake_move_event]
        GLib.timeout_add_seconds(1, self.make_event_cb)
    def fake_move_event(self):
        self._az += random.randint(-90, 90) / 9.0 + (90 - self._az) / 18.0
        self._el += random.randint(-90, 90) / 9.0 + (90 - self._el) / 18.0
        self.mv_event(self._az, self._el)
    def mv_event(self, az, el, name="srt"):
        event = {
            "type": "move",
            "name": name,
            "az": az,
            "el": el,
        }
        self.emit("event::move", event)
    def make_event_cb(self):
        i = random.randint(0, len(self._fake_events) - 1)
        self._fake_events[i]()
        return True

def main():
    path = sys.argv[1]
    uri = GLib.filename_to_uri(path, None)
    src = FakeSource()
    ui = srt_front.SrtUI(uri, {"Source": src})
    ui.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()

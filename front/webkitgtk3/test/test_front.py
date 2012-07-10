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

import srt_wkgtk, sys
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
        self._fake_events = [self._fake_move_event]
        GLib.timeout_add_seconds(1, self._make_event_cb)
    def _fake_move_event(self):
        self._az += random.randint(-90, 90) / 9.0 + (90 - self._az) / 18.0
        self._el += random.randint(-90, 90) / 9.0 + (90 - self._el) / 18.0
        self._mv_event(self._az, self._el)
    def _mv_event(self, az, el, name="srt"):
        event = {
            "type": "move",
            "name": name,
            "az": az,
            "el": el,
        }
        self.emit("event::move", event)
    def _make_event_cb(self):
        i = random.randint(0, len(self._fake_events) - 1)
        self._fake_events[i]()
        return True
    def quit(self):
        # might need to do more clean up work in real version
        Gtk.main_quit()

def main():
    path = sys.argv[1]
    uri = GLib.filename_to_uri(path, None)
    src = FakeSource()
    ui = srt_wkgtk.SrtUI(uri, {"Source": src})
    ui.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()

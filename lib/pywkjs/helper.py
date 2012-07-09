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

from gi.repository import GWebKitJS as _gwkjs, GObject, WebKit

from pywkjs.general import *

class Helper(GObject.Object):
    __gsignals__ = {
        "window-object-cleared": (GObject.SignalFlags.RUN_FIRST,
                                  GObject.TYPE_NONE,
                                  (WebKit.WebFrame, GObject.TYPE_PYOBJECT))
    }
    def __init__(self, view):
        super().__init__()
        self._helper = _gwkjs.Helper.new(view)
        self._helper.connect("window-object-cleared", self._win_obj_cb)
    def _win_obj_cb(self, helper, frame, ctx, obj):
        self.emit("window-object-cleared", frame, js2py(ctx, obj))
    def get_view(self):
        return self._helper.get_view()
    def get_global(self):
        ctx = self._helper.get_context()
        obj = self._helper.get_global()
        return js2py(ctx, obj)

def new_js_global(pyobj=None, name=None):
    if not pyobj is None:
        class tmpclass(WKPYObject):
            def __init__(self):
                super().__init__()
                self.set_pyobj(pyobj)
        if not name is None:
            _gwkjs.Base.set_name(tmpclass, name)
    else:
        tmpclass = None
    ctx = _gwkjs.Context.new(tmpclass)
    obj = ctx.get_global()
    return WKJSObject(ctx, obj, jsthis=obj)

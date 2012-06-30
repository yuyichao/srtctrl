from gi.repository import GWebKitJS as _gwkjs, GObject, WebKit

from pywkjs.general import *

class Helper(GObject.GObject):
    __gsignals__ = {
        "window-object-cleared": (GObject.SIGNAL_RUN_FIRST,
                                  GObject.TYPE_NONE,
                                  (WebKit.WebFrame, GObject.TYPE_PYOBJECT))
    }
    def __init__(self, view):
        self._helper = _gwkjs.Helper.new(view)
        self._helper.connect("window-object-cleared", self._win_obj_cb)
    def _win_obj_cb(self, helper, frame, ctx, obj):
        self.emit("window-object-cleared", frame, js2py(ctx, obj))
    def get_view(self):
        return self._helper.get_view()

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

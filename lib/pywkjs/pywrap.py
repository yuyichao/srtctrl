from gi.repository import (GWebKitJS as _gwkjs)

from pywkjs.general import *

class WKPYObject(_gwkjs.Base):
    def __init__(self, pyobj):
        self._pyobj = pyobj
    def do_has_property(self, ctx, name):
        if name in self._pyobj or hasattr(self._pyobj, name):
            return True
        try:
            iname = int(name)
        except ValueError:
            return False
        if iname in self._pyobj or hasattr(self._pyobj, iname):
            return True
        return False
    def do_get_property(self, ctx, name):
        try:
            value = self._pyobj[name]
            return py2js(value)
        except:
            pass
        try:
            value = getattr(self._pyobj, name)
            return py2js(value)
        except:
            pass
        try:
            iname = int(name)
        except ValueError:
            return None
        try:
            value = self._pyobj[iname]
            return py2js(value)
        except:
            pass
        try:
            value = getattr(self._pyobj, iname)
            return py2js(value)
        except:
            pass
        return None
    def do_set_property(self, ctx, name, value):
        value = js2py(value, jsthis=self)
        try:
            if name in self._pyobj:
                self._pyobj[name] = value
                return True
        except:
            pass
        try:
            if hasattr(self._pyobj, name):
                setattr(self._pyobj, name, value)
                return True
        except:
            pass
        try:
            iname = int(name)
        except ValueError:
            try:
                self._pyobj[name] = value
                return True
            except:
                try:
                    setattr(self._pyobj, name, value)
                    return True
                except:
                    pass
                return False
        try:
            if iname in self._pyobj:
                self._pyobj[iname] = value
                return True
        except:
            pass
        try:
            if hasattr(self._pyobj, iname):
                setattr(self._pyobj, iname, value)
                return True
        except:
            pass
        try:
            self._pyobj[name] = value
            return True
        except:
            try:
                setattr(self._pyobj, name, value)
                return True
            except:
                pass
            return False
    def do_delete_property(self, ctx, name):
        pass
    def do_get_property_names(self, ctx):
        pass
    def do_call_function(self, ctx, this, args):
        pass
    def do_has_instance(self, ctx, args):
        pass
    def do_has_instance(self, ctx, ins):
        pass
    def do_convert_to(self, ctx, jstype):
        pass

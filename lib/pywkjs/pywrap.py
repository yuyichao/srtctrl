from gi.repository import GWebKitJS as _gwkjs

from pywkjs.general import *

class WKPYObject(_gwkjs.Base):
    @classmethod
    def new(klass, ctx, pyobj):
        self = ctx.make_object(klass)
        self.set_pyobj(pyobj)
    def set_pyobj(self, pyobj):
        self._pyobj = pyobj
    def do_has_property(self, ctx, name):
        try:
            if name in self._pyobj or hasattr(self._pyobj, name):
                return True
        except TypeError:
            pass
        try:
            iname = int(name)
        except ValueError:
            return False
        try:
            if iname in self._pyobj or hasattr(self._pyobj, iname):
                return True
        except TypeError:
            pass
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
            return
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
        try:
            del self._pyobj[name]
        except:
            pass
        try:
            delattr(self._pyobj, name)
        except:
            pass
        try:
            iname = int(name)
        except ValueError:
            return
        try:
            del self._pyobj[iname]
        except:
            pass
        try:
            delattr(self._pyobj, iname)
        except:
            pass
        return not self.do_has_property(ctx, name)
    def do_get_property_names(self, ctx):
        names = dir(self._pyobj)
        return _gwkjs.util_list_to_obj(names)
    def do_call_function(self, ctx, this, args):
        return self.do_call_construct(ctx, args)
    def do_call_construct(self, ctx, args):
        try:
            res = self._pyobj(*args)
            return py2js(res)
        except:
            pass
    def do_has_instance(self, ctx, ins):
        if (isinstance(self._pyobj, type) and
            isinstance(js2py(ins), self._pyobj)):
            return True
        return False
    def do_convert_to(self, ctx, jstype):
        if jstype == _gwkjs.ValueType.NUMBER:
            try:
                return ctx.make_number(float(self._pyobj))
            except:
                pass
            return
        if jstype == _gwkjs.ValueType.STRING:
            try:
                return ctx.make_string(str(self._pyobj))
            except:
                pass
            return
_gwkjs.Base.set_name(WKPYObject, "WKPYObject")

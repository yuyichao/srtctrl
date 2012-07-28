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

from __future__ import print_function, division
from gi.repository import GWebKitJS as _gwkjs

import pywkjs

def js2py(*args, **kwargs):
    return pywkjs.general.js2py(*args, **kwargs)
def py2js(*args, **kwargs):
    return pywkjs.general.py2js(*args, **kwargs)

class WKPYObject(_gwkjs.Base):
    @classmethod
    def new(klass, ctx, pyobj):
        self = ctx.make_object(klass)
        self.set_pyobj(pyobj)
        return self
    def set_pyobj(self, pyobj):
        self._pyobj = pyobj
    def do_has_property(self, ctx, name):
        # come on, why do u need to access private field....
        if name.startswith('_'):
            return False
        try:
            if name in self._pyobj:
                return True
        except TypeError:
            pass
        if hasattr(self._pyobj, name):
            return True
        if name == 'toString':
            return True
        try:
            iname = int(name)
        except ValueError:
            return False
        try:
            if iname in self._pyobj:
                return True
        except TypeError:
            pass
        if hasattr(self._pyobj, iname):
            return True
        return False
    def do_get_property(self, ctx, name):
        if name.startswith('_'):
            return
        try:
            value = self._pyobj[name]
            return py2js(ctx, value)
        except:
            pass
        try:
            value = getattr(self._pyobj, name)
            return py2js(ctx, value)
        except:
            pass
        if name == 'toString':
            def tostr(*args):
                string = str(self._pyobj)
                print("tostr: ", string)
                return py2js(ctx, string)
            return py2js(ctx, tostr)
        try:
            iname = int(name)
        except ValueError:
            return
        try:
            value = self._pyobj[iname]
            return py2js(ctx, value)
        except:
            pass
        try:
            value = getattr(self._pyobj, iname)
            return py2js(ctx, value)
        except:
            pass
    def do_set_property(self, ctx, name, value):
        if name.startswith('_'):
            return False
        value = js2py(ctx, value, jsthis=self)
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
        args = _gwkjs.util_get_argv(args)
        args = [js2py(ctx, arg) for arg in args]
        try:
            res = self._pyobj(*args)
            return py2js(ctx, res)
        except:
            pass
    def do_has_instance(self, ctx, ins):
        if (isinstance(self._pyobj, type) and
            isinstance(js2py(ctx, ins), self._pyobj)):
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

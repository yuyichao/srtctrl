from gi.repository import GObject, GLib

from .srtconf import *

class SrtBase(GObject.Object):
    __gsignals__ = {
        'error': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
                  (GObject.TYPE_INT, GObject.TYPE_STRING)),
        'update-conf': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                        (GObject.TYPE_PYOBJECT,))
    }
    _conf = {}
    def __init__(self, conf={}):
        super().__init__()
        self.__init_conf__(conf)
    def __init_conf__(self, conf):
        klass = type(self)
        _mro = klass.mro()
        _mro.reverse()
        _conf = {}
        for _type in _mro:
            try:
                _conf.update(_type._conf)
            except (TypeError, AttributeError):
                pass
        if type(conf) == str:
            g = {}
            l = {}
            execfile(conf, g, l)
            conf = l
        else:
            conf = conf.copy()
        conf.update(def_cfg)
        self._conf = update_select(conf, _conf)
    def __getattr__(self, key):
        try:
            return self._conf[key]
        except KeyError:
            raise AttributeError(key)
    def __setattr__(self, key, value):
        if (not key.startswith('_')) and key in self._conf:
            raise TypeError("Attribute %s is read-only, please use update_conf "
                            "change it.")
        GObject.GObject.__setattr__(self, key, value)
    def update_conf(self, conf):
        self.freeze_notify()
        self.emit('update-conf', conf)
        changed, self._conf = update_select_diff(conf, self._conf)
        if changed:
            self.notify('conf')
        self.thaw_notify()

    def get_conf(self):
        return self._conf.copy()
    conf = GObject.Property(
        getter=get_conf,
        flags=GObject.PARAM_READABLE,
        nick='Configuration.',
        blurb='Configuration interested in and used by this SrtObject.')

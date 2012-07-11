#!/usr/bin/env python

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

from gi.repository import GObject
from srt_comm import *

class SrtConf(GObject.Object):
    __gsignals__ = {
        "updated": (GObject.SignalFlags.RUN_FIRST,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_STRING, GObject.TYPE_STRING)),
    }
    def __init__(self, path=config.srt_config_path):
        super().__init__()
        paths = path.split(':')
        self._config = {}
        self._files = ls_dirs(paths=paths, regex='\\.py$')
    def _load_file(self, name):
        if name in self._config:
            return
        self._config[name] = {}
        for f in self._files:
            if not f.endswith('/%s.py' % name):
                continue
            g = {}
            l = {}
            try:
                execfile(f, g, l)
            except:
                pass
            l.update(self._config[name])
            self._config[name] = l
    def _get_config(self, field, key):
        self._load_file(field)
        try:
            return self._config[field][key]
        except KeyError:
            return
    def __getattr__(self, field):
        if field.startswith('_') or '/' in field:
            raise AttributeError("Attribute %s not found" % field)
        def _getter(key):
            value = self._get_config(field, key)
            if value is None:
                raise AttributeError("Attribute %s not found" % field)
            return value
        def _setter(key, value):
            self._load_file(field)
            self._config[field][key] = value
            self.emit('updated', field, key)
        return new_wrapper(_getter, _setter)
    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
            return
        raise AttributeError("Attribute %s read only" % key)
    def __getitem__(self, key):
        return self.__getattr__(str(key))

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
                    (GObject.TYPE_STRING,)),
    }
    def __init__(self, path=config.srt_config_path):
        paths = path.split(':')
        self._config = {}
        self._files = ls_dirs(paths=paths, regex='\\.py$')
        self._loaded_index = -1
    def _load_next(self):
        self._loaded_index += 1
        if self._loaded_index >= len(self._files):
            return False
        fname = self._files[self._loaded_index]
        g = {}
        l = {}
        try:
            execfile(fname, g, l)
        except:
            pass
        l.update(self._config)
        self._config = l
        return True
    def _get_config(self, key):
        while not key in self._config:
            if not self._load_next():
                break
        try:
            return self._config[key]
        except KeyError:
            return
    def __getattr__(self, key):
        if key.startswith('_'):
            raise AttributeError("Attribute %s not found" % key)
        value = self._get_config(key)
        if value is None:
            raise AttributeError("Attribute %s not found" % key)
        return value
    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
            return
        self._config[key] = value
        self.emit('updated', key)
    def __getitem__(self, key):
        return self.__getattr__(key)
    def __setitem__(self, key, value):
        if key.startswith('_'):
            raise KeyError("Cannot set key %s" % key)
        self.__setattr__(key, value)

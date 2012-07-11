# coding=utf-8

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

from srt_comm import *

class SrtPlugins:
    def __init__(self, path=config.srt_modules_path):
        paths = path.split(':')
        self._ftable = {}
        self._files = ls_dirs(paths=paths, regex='\\.py$')
        self._loaded_index = -1
        self._wrapper = new_wrapper2(self.__getter__, self.__setter__)
    def __getter__(self, key1, key2):
        iface = self._get_iface(key1, key2)
        if iface is None:
            raise AttributeError("Interface %s of type %s not found" %
                                 (key1, key2))
        return iface
    def __setter__(self, key1, key2, value):
        if not key1 in self._ftable:
            self._ftable[key1] = {}
        if not key2 in self._ftable[key1]:
            self._ftable[key1][key2] = value
        else:
            raise AttributeError("Interface %s of type %s cannot be overloaded" %
                                 (key1, key2))
    def _load_next(self):
        self._loaded_index += 1
        if self._loaded_index >= len(self._files):
            return False
        fname = self._files[self._loaded_index]
        try:
            l = {'iface': self._wrapper}
            g = {'iface': self._wrapper}
            execfile(fname, g, l)
            g.update(l)
        except Exception as err:
            print("load_next: %s" % fname, err)
        return True
    def _get_iface(self, key, name):
        while not (key in self._ftable and name in self._ftable[key]):
            if not self._load_next():
                break
        try:
            return self._ftable[key][name]
        except KeyError as err:
            print("get_iface:", err)
            return
    def __getattr__(self, key1):
        if key1.startswith('_'):
            raise AttributeError("Attribute %s not found" % key)
        def _getter(key2):
            return self.__getter__(key1, key2)
        # disable setting iface from host for now.
        # def _setter(key2, value):
        #     self.__setter__(key1, key2, value)
        return new_wrapper(_getter, None)
    def __getitem__(self, key):
        return self.__getattr__(key)

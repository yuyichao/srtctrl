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
        self._getter = new_wrapper_tree(self.__getter__, None,
                                        direr=self.__direr__)
        self._setter = new_wrapper_tree(None, self.__setter__)
    def _check_iface(self, *keys):
        try:
            self._try_get_iface(*keys)
            return True
        except KeyError:
            return False
    def _get_iface(self, *keys):
        try:
            res = self._try_get_iface(*keys)
            return res
        except KeyError:
            pass
        while not self._check_iface(*keys):
            if not self._load_next():
                break
        res = self._try_get_iface(*keys)
        return res
    def __direr__(self, *keys):
        return list(dict.keys(self._get_iface(*keys)))
    def __getter__(self, *keys):
        res = self._get_iface(*keys)
        if isinstance(res, dict):
            raise TreeHasChild
        return res
    def __setter__(self, value, *keys):
        ftable = self._ftable
        for key in keys[:-1]:
            if not key in ftable:
                ftable[key] = {}
            ftable = ftable[key]
        if not keys[-1] in ftable:
            ftable[keys[-1]] = value
        else:
            raise AttributeError("Interface %s cannot be overloaded" % str(keys))
    def _load_next(self):
        self._loaded_index += 1
        if self._loaded_index >= len(self._files):
            return False
        fname = self._files[self._loaded_index]
        try:
            l = {'setiface': self._setter, 'getiface': self._getter}
            g = {'setiface': self._setter, 'getiface': self._getter}
            execfile(fname, g, l)
            g.update(l)
        except Exception as err:
            print("load_next: %s" % fname, err)
        return True
    def _try_get_iface(self, *keys):
        ftable = self._ftable
        for key in keys:
            ftable = ftable[key]
        return ftable
    def __getattr__(self, key):
        if key.startswith('_'):
            raise AttributeError("Attribute %s not found" % key)
        return self._getter[key]
    def __getitem__(self, key):
        return self.__getattr__(key)

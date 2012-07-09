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

from srt_comm import config

def new_wrapper(getter, setter):
    class _wrapper(object):
        def __getattr__(self, key):
            if key.startswith('_'):
                raise AttributeError("Attribute %s not found" % key)
            return getter(key)
        def __setattr__(self, key, value):
            if key.startswith('_'):
                raise AttributeError("Attribute %s is read-only" % key)
            setter(key, value)
    return _wrapper()

def new_wrapper2(getter, setter):
    def _getter(key1):
        def __getter(key2):
            return getter(key1, key2)
        def __setter(key2, value):
            setter(key1, key2, value)
        return new_wrapper(__getter, __setter)
    def _setter(key1, value):
        raise AttributeError("Attribute %s is read-only" % key2)
    return new_wrapper(_getter, _setter)

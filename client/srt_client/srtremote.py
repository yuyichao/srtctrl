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

import os, socket, fcntl
from time import sleep

from srt_comm import *

class SrtRemote(SrtConn):
    __gsignals__ = {
        "error": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_INT, GObject.TYPE_STRING)),
        "initialized": (GObject.SignalFlags.RUN_FIRST,
                        GObject.TYPE_NONE,
                        (GObject.TYPE_STRING,)),
        "got-obj": (GObject.SignalFlags.RUN_FIRST,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_PYOBJECT,)),
    }
    def __init__(self):
        super.__init__()
        self._dispatch = None
        self._name = None
        self._plugins = SrtPlugins()
    def _disconn_cb(self):
        self.emit('error', SRTERR_CONN, 'disconnected')
    def _conn_cb(self, success, init):
        if not success:
            self.emit('error', SRTERR_CONN, 'cannot connect')
            return
        if not self.start_send():
            self.emit('error', SRTERR_CONN, 'cannot send')
            return
        self._plugins.initializer[init](self)
    def init(self, addr, init=config.srt_initializer):
        self.conn_recv(addr, self._conn_cb, init)
    def set_dispatch(self, dispatch):
        self._dispatch = dispatch
    def _do_dispatch(self, buff):
        try:
            return self._dispatch(buff)
        except:
            return super()._do_dispatch(buff)
    def set_name(self, name):
        if not self._name is None:
            raise AttributeError('name is already set')
        self._name = name
        if name is None:
            self.emit('error', SRTERR_PLUGIN, 'cannot decide type '
                      'of remote server')
            return
        try:
            self._protocol = self._plugins.protocol[name](self)
        except:
            self.emit('error', SRTERR_PLUGIN, 'protocol [%s] cannot be loaded' %
                      name)
            return
        self.emit('initialized', name)
    def feed_obj(self, obj):
        self.emit('got-obj', obj)
    def busy(self):
        self.emit('error', SRTERR_BUSY, 'remote server busy')

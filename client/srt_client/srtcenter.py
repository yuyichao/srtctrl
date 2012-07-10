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
from srt_comm import config as glob_conf
from gi.repository import GObject

class SrtCenter(GObject.Object):
    def __init__(self, config={}):
        super().__init__()
        self._config = SrtConfig()
        try:
            for key, value in config.items():
                try:
                    self._config[key] = value
                except KeyError:
                    pass
        except:
            pass
        self._remote = SrtRemote()
        self._remote.connect('error', self._remote_err_cb)
        self._remote.connect('initialized', self._remote_init_cb)
        self._remote.connect('ready', self._remote_ready_cb)
        self._remote.connect('got-obj', self._remote_got_obj_cb)
    def _remote_err_cb(self, remote, errno, msg):
        pass
    def _remote_init_cb(self, remote, name):
        pass
    def _remote_ready_cb(self, remote):
        pass
    def _remote_got_obj_cb(self, remote, obj):
        pass
    def init(self):
        host = str(self._config.host)
        port = int(self._config.port)
        init = None
        try:
            init = str(self._config.initializer)
        except:
            pass
        if init is None:
            self._remote.init((host, port))
        else:
            self._remote.init((host, port), init=init)

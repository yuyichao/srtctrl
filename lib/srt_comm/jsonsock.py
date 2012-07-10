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

from srt_comm.srtconn import SrtConn
from srt_comm.jsonstm import get_json
from gi.repository import GObject
import json

class JSONSock(SrtConn):
    __gsignals__ = {
        "got-obj": (GObject.SignalFlags.RUN_FIRST,
                    GObject.TYPE_NONE,
                    (GObject.TYPE_PYOBJECT,))
    }
    def __init__(self, sfamily=None, stype=None, sprotocol=None, fd=None,
                 **kwargs):
        super().__init__(sfamily=sfamily, stype=stype, sprotocol=sprotocol,
                         fd=fd, **kwargs)
        self.connect('package', __class__._got_pkg_cb)
    def _do_dispatch(self, buff):
        (extra, pkg, left) = get_json(buff)
        return (pkg, left)
    def _got_pkg_cb(self, pkg):
        try:
            obj = json.loads(pkg)
        except ValueError:
            pass
        self.emit('got-obj', obj)
    def recv(self):
        while True:
            pkg = super().recv()
            if not pkg:
                return
            try:
                return json.loads(pkg)
            except ValueError:
                pass
    def send(self, obj):
        try:
            pkg = json.dumps(obj)
        except TypeError:
            return
        super().send(pkg)

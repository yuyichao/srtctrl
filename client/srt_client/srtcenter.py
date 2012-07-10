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
from gi.repository import GObject, GLib

class SrtCenter(GObject.Object):
    __gsignals__ = {
        "quit": (GObject.SignalFlags.RUN_FIRST,
                 GObject.TYPE_NONE,
                 ()),
        "error": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  (GObject.TYPE_INT, GObject.TYPE_STRING)),
    }
    def __init__(self, config={}):
        super().__init__()
        self._mainloop = GLib.MainLoop()
        self.__init_config__(config)
        self.__init_remote__()
        self.__init_helper__()

    def __init_config__(self, config):
        self._config = SrtConfig()
        try:
            for key, value in config.items():
                try:
                    self._config[key] = value
                except KeyError:
                    pass
        except:
            pass
    def __init_remote__(self):
        self._remote = SrtRemote()
        self._remote.connect('error', self._remote_err_cb)
        self._remote.connect('quit', self._remote_quit_cb)
        self._remote.connect('initialized', self._remote_init_cb)
        self._remote.connect('ready', self._remote_ready_cb)
        self._remote.connect('got-obj', self._remote_got_obj_cb)
    def __init_helper__(self):
        self._helper = exec_n_conn(glob_conf.srt_helper, n=1, gtype=JSONSock)[0]
        self._helper.start_send()
        self._helper.start_recv()
        self._helper.connect('disconnect', self._helper_disconn_cb)
        self._helper.connect('got-obj', self._helper_got_obj_cb)

    def _helper_got_obj_cb(self, helper, obj):
        pass
    def _helper_disconn_cb(self, helper):
        pass

    def _remote_err_cb(self, remote, errno, msg):
        self.emit('error', errno, msg)
        if errno in [SRTERR_CONN, SRTERR_BUSY, SRTERR_PLUGIN]:
            self._quit()
    def _remote_init_cb(self, remote, name):
        self._helper.send({"type": "init", "name": name})
    def _remote_ready_cb(self, remote):
        self._helper.send({"type": "ready"})
    def _remote_quit_cb(self, remote):
        self._quit()
    def _remote_got_obj_cb(self, remote, obj):
        self._helper.send({"type": "remote", "obj": obj})

    def _quit(self):
        self.emit('quit')
        self._remote.wait_send()
        self._mainloop.quit()
    def do_quit(self):
        # TODO add srthost
        self._helper.send({"type": "quit"})
        self._helper.wait_send()
        # shutdown here?
    def do_error(self, errno, msg):
        # TODO add srthost
        self._helper.send({"type": "error", "errno": errno, "msg": msg})
    def run(self):
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
        self._mainloop.run()

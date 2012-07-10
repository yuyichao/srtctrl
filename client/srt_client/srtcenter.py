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
from srt_client.srtconf import *
from srt_client.srtremote import *

class SrtCenter(GObject.Object):
    __gsignals__ = {
        "init": (GObject.SignalFlags.RUN_FIRST,
                 GObject.TYPE_NONE,
                 (GObject.TYPE_STRING,)),
        "ready": (GObject.SignalFlags.RUN_FIRST,
                  GObject.TYPE_NONE,
                  ()),
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
        self._remote_err_id = 0
        self.__init_config__(config)
        self.__init_remote__()
        self.__init_helper__()

    def __init_config__(self, config):
        self._config = SrtConf()
        try:
            for field, group in config.items():
                try:
                    for key, value in group.items():
                        try:
                            self._config[field][key] = value
                        except:
                            pass
                except:
                    pass
        except:
            pass
    def __init_remote__(self):
        if self._remote_err_id:
            self._remote.disconnect(self._remote_err_id)
        self._remote = SrtRemote()
        self._remote_err_id = self._remote.connect('error', self._remote_err_cb)
        self._remote.connect('initialized', self._remote_init_cb)
        self._remote.connect('ready', self._remote_ready_cb)
        self._remote.connect('got-obj', self._remote_got_obj_cb)
        self._remote.connect('reconnect', self._remote_reconnect_cb)
    def __init_helper__(self):
        self._helper = exec_n_conn(glob_conf.srt_helper, n=1, gtype=JSONSock)[0]
        self._helper.start_send()
        self._helper.start_recv()
        self._helper.connect('disconn', self._helper_disconn_cb)
        self._helper.connect('got-obj', self._helper_got_obj_cb)

    def _helper_got_obj_cb(self, helper, pkg):
        try:
            pkgtype = pkg["type"]
        except:
            return
        if pkgtype == "remote":
            try:
                obj = pkg["obj"]
            except:
                return
            try:
                if pkg["type"] == "quit":
                    self._quit()
                    return
            except:
                pass
            self._remote.request(obj)
            return
        elif pkgtype == "slave":
            # TODO send to host
            pass
        elif pkgtype == "busy":
            # TODO send to host
            pass
        elif pkgtype == "ready":
            self.emit('ready')
        elif pkgtype == "got-cmd":
            # TODO send to host
            pass
        elif pkgtype == "quit":
            self._quit()
            return
        else:
            return
    def _helper_disconn_cb(self, helper):
        self.emit('error', SRTERR_HELPER_QUIT, "Helper quit")
        self._quit()

    def _remote_err_cb(self, remote, errno, msg):
        self.emit('error', errno, msg)
        if errno in [SRTERR_CONN, SRTERR_BUSY, SRTERR_PLUGIN]:
            self._quit()
    def _remote_init_cb(self, remote, name):
        self._helper.send({"type": "init", "name": name})
        self.emit('init', name)
    def _remote_ready_cb(self, remote):
        self._helper.send({"type": "ready"})
    def _remote_got_obj_cb(self, remote, obj):
        self._helper.send({"type": "remote", "obj": obj})
    def _remote_reconnect_cb(self, remote):
        self.__init_remote__()
        self._start_remote()
    def _quit(self):
        self.emit('quit')
        self._remote.wait_send()
        self._mainloop.quit()
    def do_quit(self):
        # TODO add srthost
        self._remote.request({"type": "quit"})
        self._helper.send({"type": "quit"})
        self._helper.wait_send()
        # shutdown here?
    def do_error(self, errno, msg):
        # TODO add srthost
        self._helper.send({"type": "error", "errno": errno, "msg": msg})
    def do_init(self, name):
        # TODO init host
        pass
    def do_ready(self):
        # TODO tell host
        pass
    def run(self):
        self._start_remote()
        self._mainloop.run()
    def _start_remote(self):
        host = str(self._config.generic.host)
        port = int(self._config.generic.port)
        init = None
        try:
            init = str(self._config.generic.initializer)
        except:
            pass
        if init is None:
            self._remote.init((host, port))
        else:
            self._remote.init((host, port), init=init)

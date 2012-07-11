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

class ZwickyHelper:
    def __init__(self, helper):
        self._helper = helper
        self._reset_coor()
        self._helper.connect("config", self._config_update_cb)
        self._helper.connect("get", self._get_cb)
        self._config_dict = {}
        self._config = new_wrapper(self._config_getter, None)
        self._helper.get_config("zwicky", "az_lim")
        self._helper.get_config("zwicky", "el_lim")
        self._helper.get_config("zwicky", "az_c_per_deg")
        self._helper.get_config("zwicky", "el_c_per_deg")
        self._helper.get_config("zwicky", "pushrod")
        self._helper.get_config("zwicky", "rod_l1")
        self._helper.get_config("zwicky", "rod_l2")
        self._helper.get_config("zwicky", "rod_l3")
        self._helper.get_config("zwicky", "rod_t0")
        self._helper.get_config("zwicky", "rod_crate")
        self._helper.get_config("zwicky", "station")
        self._helper.get_config("zwicky", "curv_corr")
    def _reset_coor(self):
        self._az_c = 0
        self._el_c = 0
        self._source = False
    def _config_update_cb(self, helper, field, name, value):
        self._config_dict[name] = value
    def _config_getter(self, key):
        return get_dict_fields(self._config_dict, key)
    def _get_cb(self, helper, name, sid):
        pass
    def recv(self):
        while True:
            pkg = self._helper.wait_types("remote")
            try:
                obj = pkg["obj"]
            except:
                continue
            return self.handle_remote(obj)
    def recv_slave(self):
        while True:
            pkg = self._helper.wait_types(["remote", "slave"])
            pkgtype = pkg["type"]
            if pkgtype == "remote":
                try:
                    self.handle_remote(pkg["obj"])
                except:
                    pass
                continue
            elif pkgtype == "slave":
                sid, obj = dict_get_fields(pkg, "sid", "obj")
                if None in [sid, obj]:
                    continue
                self._helper.send_got_cmd(sid)
                return (sid, obj)

    def handle_remote(self, obj):
        # update coordinate etc and return processed data
        pass
    def send(self, obj):
        self._helper.send(obj)
        return self.recv()
    def reset(self):
        self.send({"type": "move", "direct": 0, "count": 5000})
        self.send({"type": "move", "direct": 2, "count": 5000})
        self.send({"type": "source", "on": False})
        self._reset_coor()
    def run(self):
        self._helper.wait_ready()
        self.reset()
        self._helper.send_ready()
        # while True:
        #     sid, obj = self.recv_slave()
        #     # do real work here...

def StartZwicky(helper):
    zwicky = ZwickyHelper(helper)
    zwicky.run()

iface.helper.zwicky = StartZwicky

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

from gi.repository import GLib

class Zwicky:
    def __init__(self, remote):
        self._remote = remote
        self._remote.set_dispatch(iface.dispatch.line)
        self._remote.connect('package', self._package_cb)
        self._remote.connect('request', self._request_cb)
    def _reask_busy(self):
        self._remote.send('RUBUSY?\n')
        return False
    def _package_cb(self, remote, pkg):
        seq = pkg.split()
        if not seq:
            return
        elif seq[0] == 'NO':
            remote.ready()
            return
        elif seq[0] == 'YES':
            remote.busy()
            return
        elif seq[0] == 'MAYBE':
            remote.reconnect()
            return
        elif seq[0] == 'BEEP':
            if len(seq) < 2:
                remote.unknown(pkg)
                return
            remote.feed_obj({"type": "beep", "host": seq[1]})
            return
        elif seq[0] == '-1':
            # probably print a error message here?
            return
        else:
            remote.send('GotIt.\n')
        if seq[0] == 'C':
            if len(seq) < 4:
                remote.unknown(pkg)
                return
            if seq[2] == '7':
                on = True
            elif seq[2] == '6':
                on = False
            else:
                remote.unknown(pkg)
                return
            remote.feed_obj({"type": "source", "on": on})
            return
        if seq[0] == 'M':
            if len(seq) < 4:
                remote.unknown(pkg)
                return
            (count, over, direct) = seq[1:4]
            try:
                rcount = int(count) + int(over)
            except ValueError:
                remote.unknown(pkg)
                return
            if not direct in ['0', '1', '2', '3']:
                remote.unknown(pkg)
                return
            direct = int(direct)
            remote.feed_obj({"type": "move", "direct": direct, "count": rcount,
                             "edge": -1})
            return
        elif seq[0] == 'T':
            if len(seq) < 4:
                remote.unknown(pkg)
                return
            (count, direct, origin) = seq[1:4]
            try:
                rcount = int(count)
            except ValueError:
                remote.unknown(pkg)
                return
            if not direct in ['0', '1', '2', '3']:
                remote.unknown(pkg)
                return
            direct = int(direct)
            remote.feed_obj({"type": "move", "direct": direct, "count": rcount,
                             "edge": direct})
            return
        elif seq[0] == '128':
            if len(seq) < 66:
                remote.unknown(pkg)
                return
            try:
                data = [int(p) for p in seq[1:65]]
            except ValueError:
                remote.unknown(pkg)
                return
            remote.feed_obj({"type": "radio", "data": data})
            return
        else:
            remote.unknown(pkg)
            return
    def _request_cb(self, remote, obj):
        try:
            reqtype = obj['type']
        except:
            remote.unknown_req(obj)
        if reqtype == 'move':
            try:
                direct = int(obj['direct'])
                count = int(obj['count'])
            except:
                remote.unknown_req(obj)
                return
            if (not 0 <= direct <= 3) or count <= 0:
                remote.unknown_req(obj)
                return
            remote.send('move %d %d  \n' % (direct, count))
            return
        elif reqtype == 'source':
            try:
                on = bool(obj['on'])
            except:
                remote.unknown_req(obj)
                return
            direct = 7 if on else 6
            remote.send('move %d %d  \n' % (direct, 0))
            return
        elif reqtype == 'radio':
            try:
                freq = int(obj['freq'])
                mode = int(obj['mode'])
            except:
                remote.unknown_req(obj)
                return
            if (not 1 <= mode <= 3) or freq <= 0:
                remote.unknown_req(obj)
                return
            remote.send('radio %d %d  \n' % (freq, mode))
            return
        elif reqtype == 'quit':
            remote.send('bye. \n')
            return
        else:
            remote.unknown_req(obj)
            return

iface.protocol.zwicky = Zwicky

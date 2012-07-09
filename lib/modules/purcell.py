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

class Purcell:
    def __init__(self, remote):
        self._remote = remote
        self._remote.set_dispatch(iface.dispatch.get_line)
        self._remote.connect('package', self._pkg_cb)
    def _pkg_cb(self, remote, pkg):
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
            remote.send('RUBUSY?\n')
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
            (count, over, direct) == seq[1:4]
            try:
                count = int(count) + int(over)
            except ValueError:
                remote.unknown(pkg)
                return
            if not direct in ['0', '1', '2', '3']:
                remote.unknown(pkg)
                return
            direct = int(direct)
            remote.feed_obj({"type": "move", "direct": direct, "count": count,
                             "edge": -1})
            return
        elif seq[0] == 'T':
            if len(seq) < 4:
                remote.unknown(pkg)
                return
            (count, over, origin) == seq[1:4]
            try:
                count = int(count)
            except ValueError:
                remote.unknown(pkg)
                return
            if not direct in ['0', '1', '2', '3']:
                remote.unknown(pkg)
                return
            direct = int(direct)
            remote.feed_obj({"type": "move", "direct": direct, "count": count,
                             "edge": direct})
            return
        elif seq[0] == '128':
            pass
        else:
            remote.unknown(pkg)
            return

iface.protocol.purcell = Purcell

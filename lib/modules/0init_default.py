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

class DefaultInit:
    def __init__(self, remote):
        self._remote = remote
        self._remote.set_dispatch(self._dispatch)
        self._remote.send('RUBUSY?\n')
    def _dispatch(self, buff):
        buff = buff.lstrip()
        if not buff:
            return ('', '')
        if buff[0].isalpha():
            self._remote.set_dispatch(getiface.dispatch.line)
            self._remote.set_name('zwicky')
            return getiface.dispatch.line(buff)
        if buff[0] in '([{':
            pkg, left = getiface.dispatch.json(buff)
            if not pkg:
                return pkg, left
            self._remote.set_dispatch(getiface.dispatch.json)
            import json
            try:
                obj = json.loads(pkg)
            except ValueError:
                self._remote.set_name(None)
                return pkg, left
            if not 'name' in obj:
                # don't really like this
                self._remote.set_name('purcell')
            else:
                self._remote.set_name(obj['name'])
            return pkg, left
        self._remote.set_name(None)
        return super()._do_dispatch(buff)

setiface.initializer.default = DefaultInit

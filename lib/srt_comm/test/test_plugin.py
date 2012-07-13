#!/usr/bin/env python

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

print(config.srt_modules_path)
plugins = SrtPlugins()
print(plugins._files)
print('plugin created')
# print(plugins.test.f2.fd.jk.ji)
# print(plugins.test)
# print(plugins.test.func1())
# print(plugins.test.func2(4))
# print(plugins.test2.func3())
# print(plugins.test3['aaa'])
# print(plugins.initializer['default'])

print(plugins.a.d)
print(dir(plugins.props.zwicky))
for p in plugins.props.zwicky:
    print(p)

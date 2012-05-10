#!/usr/bin/env python

# Copyright 2012 Yu Yichao
# yyc1992@gmail.com
#
# This file is part of SrtCtrl.
#
# SrtCtrl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SrtCtrl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SrtCtrl.  If not, see <http://www.gnu.org/licenses/>.

# This file incorporates work covered by the following copyright and
# permission notice:
#
#     Copyright (c) 2007, Simon Edwards <simon@simonzone.com>
#     Redistribution and use is allowed according to the terms of the BSD
#     license. For details see the accompanying COPYING-CMAKE-SCRIPTS file.

import sys, distutils.sysconfig, imp

print("exec_prefix:%s" % sys.exec_prefix)
print("short_version:%s" % sys.version[:3])
print("long_version:%s" % sys.version.split()[0])
print("py_inc_dir:%s" % distutils.sysconfig.get_python_inc())
print("site_packages_dir:%s" %
      distutils.sysconfig.get_python_lib(plat_specific=1))
try:
    magic_tag = imp.get_tag()
except AttributeError:
    magic_tag = ''
print("magic_tag:%s" % magic_tag)

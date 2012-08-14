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

from __future__ import print_function, division
from .util import *
from math import *

def sind(t):
    return sin(t * (pi / 180))
def cosd(t):
    return cos(t * (pi / 180))
def tand(t):
    return tan(t * (pi / 180))
def cotd(t):
    return 1 / tand(t)
def secd(t):
    return 1 / cosd(t)
def cscd(t):
    return 1 / sind(t)
def arcsind(t):
    return asin(t) / (pi / 180)
def arccosd(t):
    return acos(t) / (pi / 180)
def arctand(t):
    return atan(t) / (pi / 180)
def arctan2d(y, x):
    return (atan2(y, x) / (pi / 180)) % 360
def arccotd(t):
    return arctand(1 / t)
def arcsecd(t):
    return arccosd(1 / t)
def arccscd(t):
    return arcsind(1 / t)

def rot_2d(x, y, agl):
    return [x * cosd(agl) + y * sind(agl),
            y * cosd(agl) - x * sind(agl)]

def absagl(t):
    return abs((t + 180) % 360 - 180)

def ae2xyz_zx(ae):
    [az, el] = ae
    return [cosd(el) * sind(az), sind(el), cosd(el) * cosd(az)]
def xyz2ae_zx(xyz):
    [x, y, z] = xyz
    r = sqrt(x**2 + z**2)
    if r == 0:
        return [0, 90]
    else:
        return [arctan2d(x, z), arctand(y / r)]
def ae2xyz_xy(ae):
    [az, el] = ae
    return [cosd(el) * cosd(az), cosd(el) * sind(az), sind(el)]
def xyz2ae_xy(xyz):
    [x, y, z] = xyz
    r = sqrt(x**2 + y**2)
    if r == 0:
        return [0, 90]
    else:
        return [arctan2d(y, x), arctand(z / r)]
def xyz_in_ae_zx(xyz, ae):
    [az, el] = ae
    [x, y, z] = xyz
    es = [[cosd(az), 0, -sind(az)],
          [-sind(el) * sind(az), cosd(el), -sind(el) * cosd(az)],
          [cosd(el) * sind(az), sind(el), cosd(el) * cosd(az)]]
    nxyz = [es[0][i] * x + es[1][i] * y + es[2][i] * z
            for i in range(3)]
    return nxyz
def xyz_out_ae_zx(xyz, ae):
    [az, el] = ae
    [x, y, z] = xyz
    es = [[cosd(az), 0, -sind(az)],
          [-sind(el) * sind(az), cosd(el), -sind(el) * cosd(az)],
          [cosd(el) * sind(az), sind(el), cosd(el) * cosd(az)]]
    nxyz = [es[i][0] * x + es[i][1] * y + es[i][2] * z
            for i in range(3)]
    return nxyz

def xyz_in_ae_xy(xyz, ae):
    [az, el] = ae
    [x, y, z] = xyz
    es = [[cosd(el) * cosd(az), cosd(el) * sind(az), sind(el)],
          [-sind(az), cosd(az), 0],
          [-sind(el) * cosd(az), -sind(el) * sind(az), cosd(el)]]
    nxyz = [es[0][i] * x + es[1][i] * y + es[2][i] * z
            for i in range(3)]
    return nxyz
def xyz_out_ae_xy(xyz, ae):
    [az, el] = ae
    [x, y, z] = xyz
    es = [[cosd(el) * cosd(az), cosd(el) * sind(az), sind(el)],
          [-sind(az), cosd(az), 0],
          [-sind(el) * cosd(az), -sind(el) * sind(az), cosd(el)]]
    nxyz = [es[i][0] * x + es[i][1] * y + es[i][2] * z
            for i in range(3)]
    return nxyz

def ae_with_offset_as(ae_b, offset,
                      base_type='xy', offset_type='xy', comp_type='xy'):
    if base_type == 'zx':
        ae2xyz = ae2xyz_zx
    else:
        ae2xyz = ae2xyz_xy
    if offset_type == 'zx':
        xyz_in_ae = xyz_in_ae_zx
    else:
        xyz_in_ae = xyz_in_ae_xy
    if comp_type == 'zx':
        xyz2ae = xyz2ae_zx
    else:
        xyz2ae = xyz2ae_xy
    in_xyz = ae2xyz(offset)
    out_xyz = xyz_in_ae(in_xyz, ae_b)
    return xyz2ae(out_xyz)

def ae_offset_of(ae_b, ae,
                 base_type='xy', offset_type='xy', comp_type='xy'):
    if comp_type == 'zx':
        ae2xyz = ae2xyz_zx
    else:
        ae2xyz = ae2xyz_xy
    if offset_type == 'zx':
        xyz_out_ae = xyz_out_ae_zx
    else:
        xyz_out_ae = xyz_out_ae_xy
    if base_type == 'zx':
        xyz2ae = xyz2ae_zx
    else:
        xyz2ae = xyz2ae_xy
    out_xyz = ae2xyz(ae)
    in_xyz = xyz_out_ae(out_xyz, ae_b)
    return xyz2ae(in_xyz)

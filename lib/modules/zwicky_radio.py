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
# Hard code these numbers now.

base_freqsep = 0.0078125
mmodsep_c = 9
mmodsep_bin = 46
rolloff = 7
gray_corr_half = [1.000000, 1.006274, 1.022177, 1.040125, 1.051102, 1.048860,
                  1.033074, 1.009606, 0.987706, 0.975767, 0.977749, 0.991560,
                  1.009823, 1.022974, 1.023796, 1.011319, 0.991736, 0.975578,
                  0.972605, 0.986673, 1.012158, 1.032996, 1.025913, 0.968784,
                  0.851774, 0.684969, 0.496453, 0.320612, 0.183547, 0.094424,
                  0.046729, 0.026470, 0.021300]
gray_corr = r_[gray_corr_half[31::-1], gray_corr_half[1:32]]
gray_corr = gray_corr[rolloff:-rolloff]

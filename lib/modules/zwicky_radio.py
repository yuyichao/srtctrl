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

from __future__ import print_function, division
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
gray_corr = gray_corr_half[31::-1] + gray_corr_half[1:32]
gray_corr = gray_corr[rolloff:-rolloff]
overlap = (31 - rolloff) * 2 - mmodsep_bin + 1

def comb_buff(buffs, mode):
    n = len(buffs)
    if n == 1:
        return buffs[0]
    # mode 2 only now
    len_f = len(buffs[0])
    len_c = len_f - overlap
    corr = [1] * n
    for i in range(n - 1):
        corr[i + 1] = (sum(buffs[i][-overlap:]) /
                       sum(buffs[i + 1][:overlap])) * corr[i]
    n_c = int(n / 2)
    corr_c = corr[n_c]
    corr = [c / corr_c for c in corr]
    for i in range(n):
        buffs[i] = [buffs[i][j] * corr[i] for j in range(len(buffs[i]))]
    resbuff = [0] * (len_c * n + overlap)
    resbuff[:overlap] = buffs[0][:overlap]
    for i in range(n):
        for j in range(overlap):
            resbuff[len_c * i:len_c * i + overlap][j] += buffs[i][j]
            resbuff[len_c * i:len_c * i + overlap][j] /= 2
        resbuff[len_c * i + overlap:len_c * i + len_f] = buffs[i][overlap:]
    return resbuff

def fsep_from_mode(mode):
    if mode == 3:
        return base_freqsep / 4
    elif mode == 2:
        return base_freqsep / 2
    return base_freqsep

def frange_from_cfreqc(cfreqc, mode):
        fsep = fsep_from_mode(mode)
        hnum = 0 if mode in [1, 2, 3] else mode - 3
        df = (mmodsep_bin * hnum + 31 - rolloff) * fsep
        cfreq = count2cfreq(cfreqc)
        return [cfreq - df, cfreq + df]

def cfreq2count(f):
    return int(f * 25 + 20.5)

def count2cfreq(c):
    return (c - 20.5) / 25

class ZwickyRadio:
    def __init__(self, zwicky):
        self._zwicky = zwicky
        self._zwicky.get_config("curv_corr")
        self.configs = self._zwicky.configs
        self._sys_tmp = 0
        self._calib = 1
        self.set_freq(1420.4, 1)
    def corr_radio(self, data, mode):
        if not len(data) == 64:
            return
        if not mode in [1, 2, 3]:
            return
        freqsep = fsep_from_mode(mode)
        reply = data[-63:][rolloff:-rolloff]
        reply = reply[::-1]
        curv_corr_c = [.4 * freqsep * i
                       for i in range(rolloff - 31, 32 - rolloff)]
        return [(reply[i] / gray_corr[i] *
                 (1 + self.configs.curv_corr * curv_corr_c[i]**2))
                for i in range(len(reply))]
    def set_freq(self, freq, mode):
        if freq is None:
            freq = self._freq
        if mode is None:
            mode = self._mode
        if not mode in {1, 2, 3, 4, 5}:
            mode = 1
        self._freq = freq
        self._mode = mode
    def get_freq(self):
        return {"freq": self._freq, "mode": self._mode}
    def get_nfreq(self):
        if self._mode in {1, 2, 3}:
            return len(gray_corr)
        return (len(gray_corr) - overlap) * (self._mode * 2 - 5) + overlap
    def get_frange(self):
        freq, mode = self._freq, self._mode
        cfreqc = cfreq2count(freq)
        return frange_from_cfreqc(cfreqc, mode)
    def _radio(self):
        freq, mode = self._freq, self._mode
        cfreqc = cfreq2count(freq)
        r_hnum = 0 if mode in [1, 2, 3] else (mode - 3)
        r_mode = mode if mode in [1, 2, 3] else 1
        buff = []
        for i in range(r_hnum * 2 + 1):
            freqc = cfreqc + mmodsep_c * (i - r_hnum)
            res = self._zwicky.send_radio(freqc, r_mode)
            if res is None:
                return
            buff.append(res)
        return comb_buff(buff, 2)
    def radio(self):
        buff = self._radio()
        if buff is None:
            return
        return self._radio_res(buff)
    def _radio_res(self, buff):
        frange = self.get_frange()
        res = {"data": [d / self._calib for d in buff],
               "freq_range": frange}
        self._zwicky.send_signal("radio", res)
        return res
    def get_calib(self):
        return self._calib
    def get_sys_tmp(self):
        return self._sys_tmp
    def calib(self, count):
        self._zwicky.send_source(True)
        on_buff = []
        for i in range(count):
            buff = self._radio()
            if buff is None:
                return
            self._radio_res(buff)
            on_buff.append(sum(buff) / len(buff))
        self._zwicky.send_source(False)
        off_buff = []
        for i in range(count):
            buff = self._radio()
            if buff is None:
                return
            self._radio_res(buff)
            off_buff.append(sum(buff) / len(buff))

        on_mean = sum(on_buff) / len(on_buff)
        off_mean = sum(off_buff) / len(off_buff)
        self._calib = (on_mean - off_mean) / 115.
        self._sys_tmp = off_mean / self._calib
        return {"calib": self._calib, "sys_tmp": self._sys_tmp}

setiface.device.zwicky.radio = ZwickyRadio

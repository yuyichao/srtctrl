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
from gi.repository import WebKit, Gtk, GLib, GObject

def openuri(uri):
    import subprocess
    browser = 'xdg-open'
    subprocess.Popen([browser, uri])

def file_dialog(cur_file=None, save=False):
    sel_file = None
    if save:
        title = 'Save ... '
        action = Gtk.FileChooserAction.SAVE
        button = Gtk.STOCK_SAVE
    else:
        title = 'Open ... '
        action = Gtk.FileChooserAction.OPEN
        button = Gtk.STOCK_OPEN
    fc_dlg = Gtk.FileChooserDialog(title, None, action,
                                   [button, Gtk.ResponseType.OK,
                                    Gtk.STOCK_CLEAR, Gtk.ResponseType.CLOSE,
                                    Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL])
    fc_dlg.set_default_response(Gtk.ResponseType.OK)
    if cur_file:
        fc_dlg.set_filename(cur_file)
    resp = fc_dlg.run()
    if resp == Gtk.ResponseType.OK:
        sel_file =  fc_dlg.get_filename()
    elif resp == Gtk.ResponseType.CANCEL:
        sel_file = cur_file
    fc_dlg.destroy()
    return sel_file

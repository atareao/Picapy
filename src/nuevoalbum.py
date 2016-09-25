#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of picapy
#
# Copyright (C) 2010-2016 Lorenzo Carbonell

# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk
import comun
from comun import _


class NuevoAlbum(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self)
        self.set_title(_('Create new Album'))
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_modal(True)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
                         Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.set_size_request(530, 170)
        self.set_resizable(False)
        self.set_icon_name(comun.ICON)
        self.connect('destroy', self.close)

        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)

        frame0 = Gtk.Frame()
        vbox0.pack_start(frame0, False, False, 0)

        table = Gtk.Table(n_rows=3, n_columns=2, homogeneous=False)
        table.set_border_width(5)
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        frame0.add(table)

        label1 = Gtk.Label(label=_('Title')+':')
        label1.set_alignment(0, .5)
        table.attach(label1, 0, 1, 0, 1,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)

        self.entry1 = Gtk.Entry()
        self.entry1.set_width_chars(50)
        table.attach(self.entry1, 1, 2, 0, 1,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)

        label2 = Gtk.Label(label=_('Commentary')+':')
        label2.set_alignment(0, .5)
        table.attach(label2, 0, 1, 1, 2,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)

        self.entry2 = Gtk.Entry()
        self.entry2.set_width_chars(50)
        table.attach(self.entry2, 1, 2, 1, 2,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)

        label3 = Gtk.Label(label=_('Access')+':')
        label3.set_alignment(0, .5)
        table.attach(label3, 0, 1, 2, 3,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)

        model = Gtk.ListStore(str)
        model.append([_('Private')])
        model.append([_('Protected')])
        model.append([_('Public')])
        self.combobox = Gtk.ComboBox()
        self.combobox.set_model(model)
        cell = Gtk.CellRendererText()
        self.combobox.pack_start(cell, True)
        self.combobox.add_attribute(cell, 'text', 0)
        self.combobox.set_active(0)
        table.attach(self.combobox, 1, 2, 2, 3,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)
        self.show_all()

    def get_album(self):
        return self.entry1.get_text()

    def get_commentary(self):
        return self.entry2.get_text()

    def get_access(self):
        if self.combobox.get_active() == 0:
            return 'private'
        elif self.combobox.get_active() == 1:
            return 'protected'
        else:
            return 'public'

    def close(self, widget):
        self.destroy()

if __name__ == '__main__':
    nv = NuevoAlbum(None)
    nv.run()
    exit(0)

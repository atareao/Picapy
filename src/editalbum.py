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
import locale
import gettext

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

class EditAlbum(Gtk.Dialog):
    def __init__(self,parent,album):
        #
        Gtk.Dialog.__init__(self)
        self.set_title(_('Edit Album'))
        self.set_modal(True)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_size_request(510,170)
        self.set_resizable(False)
        self.connect('destroy', self.close)
        #
        vbox = Gtk.VBox(spacing = 5)
        vbox.set_border_width(5)
        self.get_content_area().add(vbox)
        #
        frame = Gtk.Frame()
        vbox.pack_start(frame,True,True,0)
        #
        table = Gtk.Table(n_rows = 4, n_columns = 2, homogeneous = False)
        table.set_border_width(5)
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        frame.add(table)
        #
        label1 = Gtk.Label.new(_('Title')+':')
        label1.set_alignment(0,0.5)
        table.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.entry1 = Gtk.Entry()
        self.entry1.set_alignment(0)
        self.entry1.set_width_chars(50)
        table.attach(self.entry1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label2 = Gtk.Label.new(_('Summary')+':')
        label2.set_alignment(0,0.5)
        table.attach(label2,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.entry2 = Gtk.Entry()
        self.entry2.set_alignment(0)
        self.entry2.set_width_chars(50)
        table.attach(self.entry2,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label3 = Gtk.Label.new(_('Access')+':')
        label3.set_alignment(0,0.5)
        table.attach(label3,0,1,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        model = Gtk.ListStore(str)
        model.append([_('Private')])
        model.append([_('Protected')])
        model.append([_('Public')])
        self.combobox = Gtk.ComboBox()
        self.combobox.set_model(model)
        cell = Gtk.CellRendererText()
        self.combobox.pack_start(cell,True);
        self.combobox.add_attribute(cell,'text',0)
        table.attach(self.combobox,1,2,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        if album != None:
            self.entry1.set_text(album.params['title'] )
            if album.params['summary'] != None:
                self.entry2.set_text(album.params['summary'] )
            if album.params['rights']  == 'public':
                self.combobox.set_active(2)
            elif album.params['rights']  == 'protected':
                self.combobox.set_active(1)
            elif album.params['rights']  == 'private':
                self.combobox.set_active(0)
        #
        self.show_all()

    def close(self,widget):
        self.destroy()

if __name__ == '__main__':
    ia = EditAlbum(None,None)
    ia.run()

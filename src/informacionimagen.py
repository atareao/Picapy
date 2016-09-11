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

from gi.repository import Gtk, Gdk
import comun
import locale
import gettext

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

class InformacionImagen(Gtk.Dialog):
    def __init__(self,parent,imagen):
        #
        Gtk.Dialog.__init__(self,)
        self.set_title(_('Information'))
        self.set_modal(True)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
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
        table = Gtk.Table(n_rows = 3, n_columns = 3, homogeneous = False)
        table.set_border_width(5)
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        frame.add(table)
        #
        label1 = Gtk.Label(label=_('Id')+':')
        label1.set_alignment(0,0.5)
        table.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.entry1 = Gtk.Entry()
        self.entry1.set_width_chars(50)
        self.entry1.set_alignment(0)
        table.attach(self.entry1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label2 = Gtk.Label(label=_('Title')+':')
        label2.set_alignment(0,0.5)
        table.attach(label2,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.entry2 = Gtk.Entry()
        self.entry2.set_width_chars(50)
        self.entry2.set_alignment(0)
        table.attach(self.entry2,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label3 = Gtk.Label(label=_('Dimensions')+':')
        label3.set_alignment(0,0.5)
        table.attach(label3,0,1,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.entry3 = Gtk.Entry()
        self.entry3.set_width_chars(50)
        self.entry3.set_alignment(0)
        table.attach(self.entry3,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label4 = Gtk.Label(label=_('Url')+':')
        label4.set_alignment(0,0.5)
        table.attach(label4,0,1,3,4, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.entry4 = Gtk.Entry()
        self.entry4.set_width_chars(50)
        self.entry4.set_alignment(0)
        table.attach(self.entry4,1,2,3,4, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.button4 = Gtk.Button()
        self.button4.connect('clicked',self.on_button4_clicked)
        self.button4.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_COPY,Gtk.IconSize.BUTTON))
        table.attach(self.button4,2,3,3,4, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label5 = Gtk.Label(label=_('Thumbnail')+' 72x72:')
        label5.set_alignment(0,0.5)
        table.attach(label5,0,1,4,5, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.entry5 = Gtk.Entry()
        self.entry5.set_width_chars(50)
        self.entry5.set_alignment(0)
        table.attach(self.entry5,1,2,4,5, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.button5 = Gtk.Button()
        self.button5.connect('clicked',self.on_button5_clicked)
        self.button5.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_COPY,Gtk.IconSize.BUTTON))
        table.attach(self.button5,2,3,4,5, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label6 = Gtk.Label(label=_('Thumbnail')+' 144x144:')
        label6.set_alignment(0,0.5)
        table.attach(label6,0,1,5,6, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.entry6 = Gtk.Entry()
        self.entry6.set_width_chars(50)
        self.entry6.set_alignment(0)
        table.attach(self.entry6,1,2,5,6, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.button6 = Gtk.Button()
        self.button6.connect('clicked',self.on_button6_clicked)
        self.button6.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_COPY,Gtk.IconSize.BUTTON))
        table.attach(self.button6,2,3,5,6, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        label7 = Gtk.Label(label=_('Thumbnail')+' 288x288:')
        label7.set_alignment(0,0.5)
        table.attach(label7,0,1,6,7, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.entry7 = Gtk.Entry()
        self.entry7.set_width_chars(50)
        self.entry7.set_alignment(0)
        table.attach(self.entry7,1,2,6,7, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
        #
        self.button7 = Gtk.Button()
        self.button7.connect('clicked',self.on_button7_clicked)
        self.button7.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_COPY,Gtk.IconSize.BUTTON))
        table.attach(self.button7,2,3,6,7, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
        #
        if imagen != None:
            self.entry1.set_text(imagen.params['id'])
            self.entry2.set_text(imagen.params['title'])
            self.entry3.set_text('%sx%s'%(imagen.params['width'],imagen.params['height']))
            self.entry4.set_text(imagen.params['url'])
            self.entry5.set_text(imagen.thumbnails[0]['url'])
            label5.set_label('%s %sx%s:'%(_('Thumbnail'),imagen.thumbnails[0]['width'],imagen.thumbnails[0]['height']))
            self.entry6.set_text(imagen.thumbnails[1]['url'])
            label6.set_label('%s %sx%s:'%(_('Thumbnail'),imagen.thumbnails[1]['width'],imagen.thumbnails[1]['height']))
            self.entry7.set_text(imagen.thumbnails[2]['url'])
            label7.set_label('%s %sx%s:'%(_('Thumbnail'),imagen.thumbnails[2]['width'],imagen.thumbnails[2]['height']))
        #
        self.show_all()

    def on_button4_clicked(self,widget):
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = widget.get_clipboard(atom)
        clipboard.set_text(self.entry4.get_text(), -1)

    def on_button5_clicked(self,widget):
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = widget.get_clipboard(atom)
        clipboard.set_text(self.entry5.get_text(), -1)

    def on_button6_clicked(self,widget):
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = widget.get_clipboard(atom)
        clipboard.set_text(self.entry6.get_text(), -1)

    def on_button7_clicked(self,widget):
        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = widget.get_clipboard(atom)
        clipboard.set_text(self.entry7.get_text(), -1)


    def close(self,widget):
        self.destroy()

if __name__ == '__main__':
    ii = InformacionImagen(None,None)
    ii.run()

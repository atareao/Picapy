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
import locale
import gettext
import comun
from comun import _
from googlepicasaapi import Picasa
from logindialog import LoginDialog
from configuration import Configuration


class Preferences(Gtk.Dialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self)
        self.set_title(_('Preferences'))
        self.set_modal(True)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
                         Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.ok = False
        self.set_size_request(400, 320)
        self.set_resizable(False)
        self.set_icon_name(comun.ICON)
        self.connect('destroy', self.close_application)

        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)

        notebook = Gtk.Notebook()
        vbox0.add(notebook)

        frame0 = Gtk.Frame()
        notebook.append_page(frame0, Gtk.Label.new(_('Login')))

        table = Gtk.Table(n_rows=2, n_columns=2, homogeneous=False)
        table.set_border_width(5)
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        frame0.add(table)

        label11 = Gtk.Label.new(_('Authorization')+':')
        label11.set_alignment(0, .5)
        table.attach(label11, 0, 1, 0, 1,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)

        self.entry1 = Gtk.Switch()
        self.entry1.connect('notify::active', self.on_entry1_activate)
        table.attach(self.entry1, 1, 2, 0, 1,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)

        frame1 = Gtk.Frame()
        notebook.append_page(frame1, Gtk.Label.new(_('Image link')))

        vbox1 = Gtk.VBox(spacing=5)
        vbox1.set_border_width(5)
        frame1.add(vbox1)

        label21 = Gtk.Label.new(_('Title')+' -> %TITLE%')
        label21.set_alignment(0, .5)
        vbox1.pack_start(label21, True, True, 0)
        label22 = Gtk.Label.new(_('Image')+' Url -> %URL%')
        label22.set_alignment(0, .5)
        vbox1.pack_start(label22, True, True, 0)
        label23 = Gtk.Label.new(_('Thumbnail')+' Url 72 pixel -> %URL72%')
        label23.set_alignment(0, .5)
        vbox1.pack_start(label23, True, True, 0)
        label24 = Gtk.Label.new(_('Thumbnail')+' Url 144 pixel -> %URL144%')
        label24.set_alignment(0, .5)
        vbox1.pack_start(label24, True, True, 0)
        label25 = Gtk.Label.new(_('Thumbnail')+' Url 288 pixel -> %URL288%')
        label25.set_alignment(0, .5)
        vbox1.pack_start(label25, True, True, 0)
        label26 = Gtk.Label.new(_('Set image link:'))
        label26.set_alignment(0, .5)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_size_request(500, 200)
        scrolledwindow.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.IN)
        vbox1.pack_start(scrolledwindow, True, True, 0)
        self.entry3 = Gtk.TextView.new()
        self.entry3.set_wrap_mode(Gtk.WrapMode.WORD)
        self.entry3.set_border_width(0)
        scrolledwindow.add(self.entry3)

        frame2 = Gtk.Frame()
        notebook.append_page(frame2, Gtk.Label.new(_('Optimization')))

        vbox2 = Gtk.VBox(spacing=5)
        vbox2.set_border_width(5)
        frame2.add(vbox2)

        hbox2 = Gtk.HBox()
        vbox2.pack_start(hbox2, False, False, 0)
        self.checkbutton21 = Gtk.CheckButton.new_with_label(
            _('Reduce size to')+':')
        hbox2.pack_start(self.checkbutton21, False, False, 0)
        self.entry4 = Gtk.Entry()
        hbox2.pack_start(self.entry4, False, False, 0)
        label41 = Gtk.Label.new(_('pixels'))
        hbox2.pack_start(label41, False, False, 0)

        self.checkbutton22 = Gtk.CheckButton.new_with_label(
            _('Gray scale')+':')
        vbox2.pack_start(self.checkbutton22, False, False, 0)

        hbox26 = Gtk.HBox()
        hbox26.set_border_width(5)
        vbox0.pack_start(hbox26, False, False, 0)

        frame3 = Gtk.Frame()
        notebook.append_page(frame3, Gtk.Label.new(_('Slideshow')))

        vbox3 = Gtk.VBox(spacing=5)
        vbox3.set_border_width(5)
        frame3.add(vbox3)

        hbox3 = Gtk.HBox()
        vbox3.pack_start(hbox3, False, False, 0)
        label_slideshow_time = Gtk.Label.new(_('Time between images')+' (s):')
        hbox3.pack_start(label_slideshow_time, False, False, 0)
        self.entry_slideshow = Gtk.SpinButton()
        self.entry_slideshow.set_adjustment(Gtk.Adjustment(
            value=0, lower=1, upper=1000, step_increment=1, page_increment=10,
            page_size=10))
        hbox3.pack_start(self.entry_slideshow, False, False, 0)

        self.load_preferences()

        self.show_all()

    def load_preferences(self):
        configuration = Configuration()
        self.image_link = configuration.get('image_link')
        max_size = configuration.get('max_size')
        reduce_size = configuration.get('reduce_size')
        reduce_colors = configuration.get('reduce_colors')
        tbi = configuration.get('time_between_images')
        ttbuffer = Gtk.TextBuffer()
        ttbuffer.set_text(self.image_link)
        self.entry3.set_buffer(ttbuffer)
        self.entry4.set_text(str(max_size))
        self.checkbutton21.set_active(reduce_size)
        self.checkbutton22.set_active(reduce_colors)
        self.entry_slideshow.set_value(tbi)
        pi = Picasa(token_file=comun.TOKEN_FILE)
        self.entry1.set_active(pi.do_refresh_authorization() is not None)

    def save_preferences(self):
        tbuffer = self.entry3.get_buffer()
        inicio = tbuffer.get_start_iter()
        fin = tbuffer.get_end_iter()
        image_link = tbuffer.get_text(inicio, fin, True)
        reduce_size = self.checkbutton21.get_active()
        max_size = self.toInt(self.entry4.get_text())
        reduce_colors = self.checkbutton22.get_active()
        tbi = self.entry_slideshow.get_value()
        configuration = Configuration()
        configuration.set('max_size', max_size)
        configuration.set('reduce_size', reduce_size)
        configuration.set('reduce_colors', reduce_colors)
        configuration.set('image_link', image_link)
        configuration.set('first_time', False)
        configuration.set('time_between_images', tbi)
        configuration.save()

    def close_application(self, widget):
        self.hide()
        self.destroy()

    def on_entry1_activate(self, widget, status):
        pi = Picasa(token_file=comun.TOKEN_FILE)
        if self.entry1.get_active():
            if pi.do_refresh_authorization() is None:
                authorize_url = pi.get_authorize_url()
                ld = LoginDialog(authorize_url)
                ld.run()
                pi.get_authorization(ld.code)
                ld.destroy()
        else:
            pi.revoke_authorization()
        self.entry1.set_active(pi.do_refresh_authorization() is not None)

    def toInt(self, valor):
        if len(valor) > 0 and valor.isdigit():
            return int(float(valor))
        else:
            return 0
if __name__ == "__main__":
    p = Preferences(None)
    if p.run() == Gtk.ResponseType.ACCEPT:
        p.save_preferences()
    p.destroy()
    exit(0)

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


from gi.repository import Gtk,GdkPixbuf
import urllib.request, urllib.parse, urllib.error
import comun
import locale
import gettext

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext


class VerImagen(Gtk.Dialog):
    def __init__(self,parent,imagen):
        Gtk.Dialog.__init__(self)
        self.set_title(_('Image'))
        self.set_modal(True)
        self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(800,800)
        self.set_resizable(True)
        self.connect('destroy', self.close)
        #
        vbox = Gtk.VBox(spacing = 5)
        vbox.set_border_width(5)
        self.get_content_area().add(vbox)
        #
        frame = Gtk.Frame()
        vbox.pack_start(frame,True,True,0)
        #
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_size_request(800,800)
        self.connect('key-release-event',self.on_key_release_event)
        frame.add(scrolledwindow)
        #
        viewport = Gtk.Viewport()
        viewport.set_size_request(800,800)
        scrolledwindow.add(viewport)
        #
        self.scale=100
        #
        #
        if imagen != None:
            f = urllib.request.urlopen(imagen.params['url'])
            data = f.read()
            pbl = GdkPixbuf.PixbufLoader()
            pbl.write(data)
            self.pbuf = pbl.get_pixbuf()
            pbl.close()
            self.image = Gtk.Image()
            self.image.set_from_pixbuf(self.pbuf)
            viewport.add(self.image)
        else:
            self.pbuf = None
        self.show_all()
        #
    def on_key_release_event(self,widget,event):
        print((event.keyval))
        if event.keyval == 65451 or event.keyval == 43:
            self.scale=self.scale*1.1
        elif event.keyval == 65453 or event.keyval == 45:
            self.scale=self.scale*.9
        elif event.keyval == 65456 or event.keyval == 48:
            self.scale = 100
        if self.pbuf != None:
            w=int(self.pbuf.get_width()*self.scale/100)
            h=int(self.pbuf.get_height()*self.scale/100)
            pixbuf=self.pbuf.scale_simple(w,h,GdkPixbuf.InterpType.BILINEAR)
            self.image.set_from_pixbuf(pixbuf)

    def close(self,widget):
        self.destroy()

if __name__ == '__main__':
    vi = VerImagen(None,None)
    vi.run()
    exit(0)

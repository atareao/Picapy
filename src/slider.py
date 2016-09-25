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
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GdkPixbuf
import urllib.request
import cairo
import time
import os
import math
import comun


def wait(time_lapse):
    time_start = time.time()
    time_end = (time_start + time_lapse)
    while time_end > time.time():
        while Gtk.events_pending():
            Gtk.main_iteration()


def load_pixbuf_from_url(url):
    opener1 = urllib.request.build_opener()
    page1 = opener1.open(url)
    data = page1.read()
    loader = GdkPixbuf.PixbufLoader()
    loader.write(data)
    loader.close()
    pixbuf = loader.get_pixbuf()
    return pixbuf


class NavigatorButton(Gtk.Button):
    def __init__(self, file_image_active, file_image_inactive):
        Gtk.Button.__init__(self)
        self.set_name('navigator_button')
        self.image_active = Gtk.Image.new_from_file(
            os.path.join(comun.IMGDIR, file_image_active+'.svg'))
        self.image_inactive = Gtk.Image.new_from_file(os.path.join(
            comun.IMGDIR, file_image_inactive+'.svg'))
        self.set_sensitive(True)

    def set_sensitive(self, sensitive):
        Gtk.Button.set_sensitive(self, sensitive)
        if sensitive:
            self.set_image(self.image_active)
        else:
            self.set_image(self.image_inactive)


class SliderWindow(Gtk.Window):
    def __init__(self, images=None, timebi=2):
        Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_icon_from_file(comun.ICON)
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.connect('key-release-event', self.on_key_release_event)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.set_default_size(250, 250)
        self.add_events(Gdk.EventMask.ALL_EVENTS_MASK)

        self.connect('draw', self.on_expose, None)
        hbox0 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox0.set_homogeneous(False)
        self.add(hbox0)
        button_previous = NavigatorButton('previous_active',
                                          'previous_inactive')
        button_previous.connect('clicked', self.on_button_previous_clicked)
        hbox0.pack_start(button_previous, False, False, 0)
        vbox1 = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox1.set_homogeneous(False)
        hbox0.pack_start(vbox1, True, True, 0)
        self.image = Gtk.Image()
        self.image.set_from_file(comun.ICON)
        vbox1.pack_start(self.image, True, True, 0)
        self.titlelabel = Gtk.Label()
        self.titlelabel.set_markup(
            "<span foreground='white' font_desc='Ubuntu 20'><b>%s</b> \
</span>" % ('uPdf'))
        vbox1.pack_start(self.titlelabel, False, False, 0)
        button_next = NavigatorButton('next_active', 'next_inactive')
        button_next.connect('clicked', self.on_button_next_clicked)
        hbox0.pack_start(button_next, False, False, 0)
        self.fullscreen()
        self._images = images
        self._timebi = timebi
        self._current_image = -1
        self._showing = False
        self.load_next_image()
        self.show_all()

    def work(self):
        if self._showing:
            self.load_next_image()
        return self._showing

    def on_key_release_event(self, widget, event):
        print(event.keyval, Gdk.keyval_name(event.keyval))
        if event.keyval == Gdk.keyval_from_name('Escape'):
            self.destroy()
        elif event.keyval == Gdk.keyval_from_name('Right') or\
                event.keyval == Gdk.keyval_from_name('KP_Right'):
            self.load_next_image()
        elif event.keyval == Gdk.keyval_from_name('Left') or\
                event.keyval == Gdk.keyval_from_name('KP_Left'):
            self.load_previous_image()
        elif event.keyval == Gdk.keyval_from_name('Up') or\
                event.keyval == Gdk.keyval_from_name('KP_Up'):
            self.load_first_image()
        elif event.keyval == Gdk.keyval_from_name('Down') or\
                event.keyval == Gdk.keyval_from_name('KP_Down'):
            self.load_last_image()
        elif event.keyval == Gdk.keyval_from_name('space'):
            if self._showing:
                self._showing = False
            else:
                self._showing = True
                GLib.timeout_add_seconds(self._timebi, self.work)

    def load_first_image(self):
        if self._images is not None:
            self._current_image = 0
            title = self._images[self._current_image].params['title']
            self.titlelabel.set_markup("<span foreground='white' \
font_desc='Ubuntu 20'><b>%s</b></span>" % (title))
            url = self._images[self._current_image].params['url']
            self.image.set_from_pixbuf(load_pixbuf_from_url(url))

    def load_previous_image(self):
        if self._images is not None:
            self._current_image -= 1
            if self._current_image < 0:
                self._current_image = len(self._images)-1
            title = self._images[self._current_image].params['title']
            self.titlelabel.set_markup("<span foreground='white' \
font_desc='Ubuntu 20'><b>%s</b></span>" % (title))
            url = self._images[self._current_image].params['url']
            self.image.set_from_pixbuf(load_pixbuf_from_url(url))

    def load_next_image(self):
        if self._images is not None:
            self._current_image += 1
            if self._current_image > (len(self._images)-1):
                self._current_image = 0
            title = self._images[self._current_image].params['title']
            self.titlelabel.set_markup("<span foreground='white' \
font_desc='Ubuntu 20'><b>%s</b></span>" % (title))
            url = self._images[self._current_image].params['url']
            self.image.set_from_pixbuf(load_pixbuf_from_url(url))

    def load_last_image(self):
        if self._images is not None:
            self._current_image = len(self._images)-1
            title = self._images[self._current_image].params['title']
            self.titlelabel.set_markup("<span foreground='white' \
font_desc='Ubuntu 20'><b>%s</b></span>" % (title))
            url = self._images[self._current_image].params['url']
            self.image.set_from_pixbuf(load_pixbuf_from_url(url))

    def on_button_next_clicked(self, widget):
        self.load_next_image()

    def on_button_previous_clicked(self, widget):
        self.load_previous_image()

    def on_expose(self, widget, cr, data):
        cr.save()
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.rectangle(0.0, 0.0, *widget.get_size())
        cr.fill()
        cr.restore()
        cr.set_source_rgba(0.0, 0.0, 0.0, .8)
        cr.rectangle(0, 0, widget.get_size()[0], widget.get_size()[1])
        cr.fill()


class yourApp():
    def __init__(self):
        self.window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        self.window.set_title('Your app name')
        self.window.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.window.connect('destroy',	Gtk.main_quit)
        main_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 1)
        main_vbox.set_homogeneous(False)
        self.window.add(main_vbox)
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox.set_homogeneous(False)

        self.lbl = Gtk.Label.new('All done! :)')
        self.lbl.set_alignment(0, 0.5)
        main_vbox.pack_start(self.lbl, True, True, 0)
        self.window.show_all()


if __name__ == "__main__":
    ss = SliderWindow()
    wait(3)
    app = yourApp()
    ss.destroy()
    Gtk.main()

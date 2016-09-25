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
from gi.repository import Gio
from gi.repository import GdkPixbuf
import urllib
import picasamod
import filters
import utils
import os
from comun import _


class EditImage(Gtk.Dialog):
    def __init__(self, parent, image):

        Gtk.Dialog.__init__(self)
        self.set_title(_('Edit Image'))
        self.set_modal(True)
        self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
                         Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_size_request(510, 170)
        self.set_resizable(False)
        self.connect('destroy', self.close)

        vbox = Gtk.VBox(spacing=5)
        vbox.set_border_width(5)
        self.get_content_area().add(vbox)

        frame = Gtk.Frame()
        vbox.pack_start(frame, True, True, 0)

        table = Gtk.Table(n_rows=5, n_columns=3, homogeneous=False)
        table.set_border_width(5)
        table.set_col_spacings(5)
        table.set_row_spacings(5)
        frame.add(table)

        label1 = Gtk.Label(label=_('Title'))
        label1.set_alignment(0, 0.5)
        table.attach(label1, 0, 1, 0, 1,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)

        self.entry1 = Gtk.Entry()
        self.entry1.set_alignment(0)
        self.entry1.set_width_chars(50)
        self.entry1.set_sensitive(False)
        table.attach(self.entry1, 1, 2, 0, 1,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)

        label2 = Gtk.Label(label=_('Summary'))
        label2.set_alignment(0, 0.5)
        table.attach(label2, 0, 1, 1, 2,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)

        self.entry2 = Gtk.Entry()
        self.entry2.set_alignment(0)
        self.entry2.set_width_chars(50)
        table.attach(self.entry2, 1, 2, 1, 2,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)

        label3 = Gtk.Label(label=_('Tags'))
        label3.set_alignment(0, 0.5)
        table.attach(label3, 0, 1, 2, 3,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)

        self.entry3 = Gtk.Entry()
        self.entry3.set_alignment(0)
        self.entry3.set_width_chars(50)
        table.attach(self.entry3, 1, 2, 2, 3,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)

        hbox = Gtk.HBox(spacing=5)
        hbox.set_border_width(5)
        table.attach(hbox, 2, 3, 2, 3,
                     xoptions=Gtk.AttachOptions.FILL,
                     yoptions=Gtk.AttachOptions.SHRINK)

        button_load_new_image = Gtk.Button()
        button_load_new_image.set_size_request(40, 40)
        button_load_new_image.set_tooltip_text(_('Load new image'))
        button_load_new_image.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'go-up-symbolic'),
            Gtk.IconSize.BUTTON))
        button_load_new_image.connect('clicked',
                                      self.on_button_clicked,
                                      'load-new-image')
        hbox.pack_start(button_load_new_image, False, False, 0)

        button_rotate_left = Gtk.Button()
        button_rotate_left.set_size_request(40, 40)
        button_rotate_left.set_tooltip_text(_('Rotate left'))
        button_rotate_left.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'object-rotate-left-symbolic'),
            Gtk.IconSize.BUTTON))
        button_rotate_left.connect('clicked',
                                   self.on_button_clicked,
                                   'rotate-left')
        hbox.pack_start(button_rotate_left, False, False, 0)

        button_rotate_right = Gtk.Button()
        button_rotate_right.set_size_request(40, 40)
        button_rotate_right.set_tooltip_text(_('Rotate right'))
        button_rotate_right.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'object-rotate-right-symbolic'),
            Gtk.IconSize.BUTTON))
        button_rotate_right.connect('clicked',
                                    self.on_button_clicked,
                                    'rotate-right')
        hbox.pack_start(button_rotate_right, False, False, 0)

        button_flip_horizontal = Gtk.Button()
        button_flip_horizontal.set_size_request(40, 40)
        button_flip_horizontal.set_tooltip_text(_('Flip horizontal'))
        button_flip_horizontal.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'object-flip-horizontal-symbolic'),
            Gtk.IconSize.BUTTON))
        button_flip_horizontal.connect('clicked',
                                       self.on_button_clicked,
                                       'flip-horizontal')
        hbox.pack_start(button_flip_horizontal, False, False, 0)

        button_flip_vertical = Gtk.Button()
        button_flip_vertical.set_size_request(40, 40)
        button_flip_vertical.set_tooltip_text(_('Flip vertical'))
        button_flip_vertical.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'object-flip-vertical-symbolic'),
            Gtk.IconSize.BUTTON))
        button_flip_vertical.connect('clicked',
                                     self.on_button_clicked,
                                     'flip-vertical')
        hbox.pack_start(button_flip_vertical, False, False, 0)

        button_grayscale = Gtk.Button()
        button_grayscale.set_size_request(40, 40)
        button_grayscale.set_tooltip_text(_('Grayscale'))
        button_grayscale.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'applications-graphics-symbolic'),
            Gtk.IconSize.BUTTON))
        button_grayscale.connect('clicked',
                                 self.on_button_clicked,
                                 'grayscale')
        hbox.pack_start(button_grayscale, False, False, 0)

        button_instagram_sunset = Gtk.Button()
        button_instagram_sunset.set_size_request(40, 40)
        button_instagram_sunset.set_tooltip_text(_('Instagram sunset'))
        button_instagram_sunset.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'weather-clear-symbolic'),
            Gtk.IconSize.BUTTON))
        button_instagram_sunset.connect('clicked',
                                        self.on_button_clicked,
                                        'instagram-sunset')
        hbox.pack_start(button_instagram_sunset, False, False, 0)

        button_instagram_colorful = Gtk.Button()
        button_instagram_colorful.set_size_request(40, 40)
        button_instagram_colorful.set_tooltip_text(_('Instagram colorful'))
        button_instagram_colorful.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'preferences-color-symbolic'),
            Gtk.IconSize.BUTTON))
        button_instagram_colorful.connect('clicked',
                                          self.on_button_clicked,
                                          'instagram-colorful')
        hbox.pack_start(button_instagram_colorful, False, False, 0)

        button_instagram_groovy = Gtk.Button()
        button_instagram_groovy.set_size_request(40, 40)
        button_instagram_groovy.set_tooltip_text(_('Instagram groovy'))
        button_instagram_groovy.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'face-smile-big-symbolic'),
            Gtk.IconSize.BUTTON))
        button_instagram_groovy.connect('clicked',
                                        self.on_button_clicked,
                                        'instagram-groovy')
        hbox.pack_start(button_instagram_groovy, False, False, 0)

        frame = Gtk.Frame()
        frame.set_size_request(600, 400)
        table.attach(frame, 0, 2, 4, 5,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_size_request(600, 400)
        frame.add(scrolledwindow)

        viewport = Gtk.Viewport()
        viewport.set_size_request(600, 400)
        scrolledwindow.add(viewport)
        self.aimage = Gtk.Image()
        viewport.add(self.aimage)

        frame2 = Gtk.Frame()
        frame2.set_size_request(600, 400)
        table.attach(frame2, 2, 3, 4, 5,
                     xoptions=Gtk.AttachOptions.EXPAND,
                     yoptions=Gtk.AttachOptions.SHRINK)
        scrolledwindow2 = Gtk.ScrolledWindow()
        scrolledwindow2.set_size_request(600, 400)
        frame2.add(scrolledwindow2)

        viewport2 = Gtk.Viewport()
        viewport2.set_size_request(600, 400)
        scrolledwindow2.add(viewport2)
        self.aimage2 = Gtk.Image()
        viewport2.add(self.aimage2)

        self.filename = None

        if image is not None:
            self.entry1.set_text(image.params['title'])
            if image.params['summary'] is not None:
                self.entry2.set_text(image.params['summary'])
            if image.params['keywords'] is not None:
                self.entry3.set_text(image.params['keywords'])
            f = urllib.request.urlopen(image.params['url'])
            data = f.read()
            pbl = GdkPixbuf.PixbufLoader()
            pbl.write(data)
            pbuf = pbl.get_pixbuf()
            pbl.close()
            if pbuf is not None:
                self.aimage.set_from_pixbuf(pbuf)
                self.aimage2.set_from_pixbuf(pbuf)
        self.show_all()

    def on_button_clicked(self, widget, operation):
        if operation == 'load-new-image':
            dialog = Gtk.FileChooserDialog(
                _('Select one images to upload to Picasa Web'),
                self,
                Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            dialog.set_default_response(Gtk.ResponseType.OK)
            filter = Gtk.FileFilter()
            filter.set_name(_('Imagenes'))
            filter.add_mime_type('image/png')
            filter.add_mime_type('image/jpeg')
            filter.add_mime_type('image/gif')
            filter.add_mime_type('image/x-ms-bmp')
            filter.add_mime_type('image/x-icon')
            filter.add_mime_type('image/tiff')
            filter.add_mime_type('image/x-photoshop')
            filter.add_mime_type('x-portable-pixmap')
            filter.add_pattern('*.png')
            filter.add_pattern('*.jpg')
            filter.add_pattern('*.gif')
            filter.add_pattern('*.bmp')
            filter.add_pattern('*.ico')
            filter.add_pattern('*.tiff')
            filter.add_pattern('*.psd')
            filter.add_pattern('*.ppm')
            dialog.add_filter(filter)
            preview = Gtk.Image()
            dialog.set_preview_widget(preview)
            dialog.connect('update-preview', self.update_preview_cb, preview)
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.filename = dialog.get_filename()
                f = open(self.filename, 'rb')
                data = f.read()
                f.close()
                pbl = GdkPixbuf.PixbufLoader()
                pbl.write(data)
                pbuf = pbl.get_pixbuf()
                pbl.close()
                if pbuf is not None:
                    self.aimage2.set_from_pixbuf(pbuf)
            dialog.destroy()
        elif operation == 'rotate-left':
            pixbuf = self.aimage2.get_pixbuf()
            if pixbuf is not None:
                pixbuf = picasamod.rotate_pixbuf(pixbuf, 90)
                self.aimage2.set_from_pixbuf(pixbuf)
        elif operation == 'rotate-right':
            pixbuf = self.aimage2.get_pixbuf()
            if pixbuf is not None:
                pixbuf = picasamod.rotate_pixbuf(pixbuf, 270)
                self.aimage2.set_from_pixbuf(pixbuf)
        elif operation == 'flip-horizontal':
            pixbuf = self.aimage2.get_pixbuf()
            if pixbuf is not None:
                pixbuf = picasamod.flip_pixbuf(pixbuf, True)
                self.aimage2.set_from_pixbuf(pixbuf)
        elif operation == 'flip-vertical':
            pixbuf = self.aimage2.get_pixbuf()
            if pixbuf is not None:
                pixbuf = picasamod.flip_pixbuf(pixbuf, False)
                self.aimage2.set_from_pixbuf(pixbuf)
        elif operation == 'grayscale':
            pixbuf = self.aimage2.get_pixbuf()
            if pixbuf is not None:
                pixbuf = picasamod.grayscale_pixbuf(pixbuf)
                self.aimage2.set_from_pixbuf(pixbuf)
        elif operation == 'instagram-sunset':
            pixbuf = self.aimage2.get_pixbuf()
            if pixbuf is not None:
                image = utils.pixbuf2image(pixbuf)
                filter = filters.CFilterSunset()
                new_image = filter.applyFilter(image)
                pixbuf = utils.image2pixbuf(new_image)
                self.aimage2.set_from_pixbuf(pixbuf)
        elif operation == 'instagram-colorful':
            pixbuf = self.aimage2.get_pixbuf()
            if pixbuf is not None:
                image = utils.pixbuf2image(pixbuf)
                filter = filters.CFilterColorful()
                new_image = filter.applyFilter(image)
                pixbuf = utils.image2pixbuf(new_image)
                self.aimage2.set_from_pixbuf(pixbuf)
        elif operation == 'instagram-groovy':
            pixbuf = self.aimage2.get_pixbuf()
            if pixbuf is not None:
                image = utils.pixbuf2image(pixbuf)
                filter = filters.CFilterGroovy()
                new_image = filter.applyFilter(image)
                pixbuf = utils.image2pixbuf(new_image)
                self.aimage2.set_from_pixbuf(pixbuf)
        else:
            pass

    def close(self, widget):
        self.destroy()

    def update_preview_cb(self, file_chooser, preview):
        filename = file_chooser.get_preview_filename()
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 128, 128)
            preview.set_from_pixbuf(pixbuf)
            have_preview = True
        except:
            have_preview = False
        file_chooser.set_preview_widget_active(have_preview)
        return

if __name__ == '__main__':
    ia = EditImage(None, None)
    ia.run()

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


import sys
import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('Gdk', '3.0')
    gi.require_version('Gio', '2.0')
    gi.require_version('GdkPixbuf', '2.0')
    gi.require_version('GObject', '2.0')
    gi.require_version('WebKit', '3.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GdkPixbuf
from gi.repository import GObject
import time
import urllib.request
import urllib.parse
import urllib.error
import configparser
import os
from os import path
import threading
import webbrowser
import time
import concurrent.futures
#
import utils
import googlepicasaapi
from googlepicasaapi import Picasa
from nuevoalbum import NuevoAlbum
from informacionalbum import InformacionAlbum
from editalbum import EditAlbum
from editimage import EditImage
from pasteimage import PasteImage
from informacionimagen import InformacionImagen
from verimagen import VerImagen
from logindialog import LoginDialog
from slider import SliderWindow
from tasker import Tasker
#
from preferences import Preferences
from progreso import Progreso
import comun
from configuration import Configuration
#
import locale
import gettext
# Reducing
import tempfile
import shutil
import re
import html.entities

import mimetypes
import json
import codecs
import cairo
import queue
from comun import _

TARGET_TYPE_TEXT = 80
TARGET_TYPE_PIXMAP = 81

NUM_THREADS = 10

PIXBUF_DEFAULT_ALBUM = GdkPixbuf.Pixbuf.new_from_file(comun.DEFAULT_ALBUM)
PIXBUF_DEFAULT_PHOTO = GdkPixbuf.Pixbuf.new_from_file(comun.DEFAULT_PHOTO)


class MainWindow (Gtk.ApplicationWindow):
    __gsignals__ = {
        'uploaded-image': (GObject.SIGNAL_RUN_FIRST,
                           GObject.TYPE_NONE,
                           (object,)),
        'uploaded-album': (GObject.SIGNAL_RUN_FIRST,
                           GObject.TYPE_NONE,
                           (object,)),
        'downloaded-image': (GObject.SIGNAL_RUN_FIRST,
                             GObject.TYPE_NONE,
                             (object,)),
        'downloaded-album': (GObject.SIGNAL_RUN_FIRST,
                             GObject.TYPE_NONE,
                             (object,)),
        }

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)
        self.set_name('MyWindow')
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_title(comun.APP)
        self.set_default_size(900, 600)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        self.app = app
        #
        self.image_dir = os.getenv('HOME')
        self.picasa = Picasa(token_file=comun.TOKEN_FILE)
        error = True
        while(error):
            if self.picasa.do_refresh_authorization() is None:
                authorize_url = self.picasa.get_authorize_url()
                ld = LoginDialog(authorize_url)
                ld.run()
                self.picasa.get_authorization(ld.code)
                ld.destroy()
                if self.picasa.do_refresh_authorization() is None:
                    md = Gtk.MessageDialog(
                        parent=self,
                        flags=(Gtk.DialogFlags.MODAL |
                               Gtk.DialogFlags.DESTROY_WITH_PARENT),
                        type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK_CANCEL,
                        message_format=_('You have to authorize Picapy to use \
it, do you want to authorize?'))
                    if md.run() == Gtk.ResponseType.CANCEL:
                        exit(3)
                else:
                    self.picasa = Picasa(token_file=comun.TOKEN_FILE)
                    if self.picasa.do_refresh_authorization() is None:
                        error = False
                    self.load_preferences()
            else:
                self.load_preferences()
                error = False
        #

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = comun.APPNAME
        self.set_titlebar(hb)

        self.button_quit = Gtk.Button()
        self.button_quit.set_tooltip_text(_('Exit'))
        self.button_quit.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'application-exit-symbolic'),
            Gtk.IconSize.BUTTON))
        self.button_quit.connect('clicked', self.close_application)
        hb.pack_start(self.button_quit)

        self.button_up = Gtk.Button()
        self.button_up.set_tooltip_text(_('Go to albums'))
        self.button_up.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'go-home-symbolic'),
            Gtk.IconSize.BUTTON))
        self.button_up.set_sensitive(False)
        self.button_up.connect('clicked', self.on_button1_clicked)
        hb.pack_start(self.button_up)

        self.button_add = Gtk.Button()
        self.button_add.set_tooltip_text(_('Add album'))
        self.button_add.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'list-add-symbolic'),
            Gtk.IconSize.BUTTON))
        self.button_add.connect('clicked', self.on_button2_clicked)
        hb.pack_start(self.button_add)

        self.button_remove = Gtk.Button()
        self.button_remove.set_tooltip_text(_('Remove album'))
        self.button_remove.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'list-remove-symbolic'),
            Gtk.IconSize.BUTTON))
        self.button_remove.connect('clicked', self.on_remove_button_clicked)
        hb.pack_start(self.button_remove)

        self.button_download = Gtk.Button()
        self.button_download.set_tooltip_text(_('Download album'))
        self.button_download.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'folder-download-symbolic'),
            Gtk.IconSize.BUTTON))
        self.button_download.connect('clicked', self.on_descargar_activated)
        hb.pack_start(self.button_download)

        self.button_slideshow = Gtk.Button()
        self.button_slideshow.set_tooltip_text(_('Slideshow'))
        self.button_slideshow.add(Gtk.Image.new_from_gicon(
            Gio.ThemedIcon.new_with_default_fallbacks(
                'applets-screenshooter-symbolic'),
            Gtk.IconSize.BUTTON))
        self.button_slideshow.set_sensitive(False)
        self.button_slideshow.connect('clicked', self.on_preview_activated)
        hb.pack_start(self.button_slideshow)

        #
        menu_button_about = Gio.Menu()
        menu_button_about.append_item(
            Gio.MenuItem.new(_('Homepage'), 'app.goto_homepage'))
        menu_button_about.append_item(
            Gio.MenuItem.new(_('Report a bug'), 'app.goto_bug'))
        menu_button_about.append_item(
            Gio.MenuItem.new(_('Make a suggestion'),
                             'app.goto_sugestion'))
        menu_button_about.append_item(
            Gio.MenuItem.new(_('Translate this application'),
                             'app.goto_translation'))
        menu_button_about.append_item(
            Gio.MenuItem.new(_('Get help online'),
                             'app.goto_questions'))
        menu_button_about.append_item(
            Gio.MenuItem.new('', None))
        menu_button_about.append_item(
            Gio.MenuItem.new(_('Follow me on Twitter'),
                             'app.goto_twitter'))
        menu_button_about.append_item(
            Gio.MenuItem.new(_('Follow me on Facebook'),
                             'app.goto_facebook'))
        menu_button_about.append_item(
            Gio.MenuItem.new(_('Follow me on Google+'),
                             'app.goto_google_plus'))
        menu_button_about.append_item(
            Gio.MenuItem.new('', None))
        menu_button_about.append_item(
            Gio.MenuItem.new(_('Donate'),
                             'app.goto_donate'))
        menu_button_about.append_item(
            Gio.MenuItem.new('', None))
        menu_button_about.append_item(
            Gio.MenuItem.new(_('About...'),
                             'app.about'))

        button_about = Gtk.MenuButton()
        button_about.add(
            Gtk.Image.new_from_gicon(
                Gio.ThemedIcon.new_with_default_fallbacks(
                    'dialog-information-symbolic'),
                Gtk.IconSize.BUTTON))
        button_about.set_menu_model(menu_button_about)
        hb.pack_end(button_about)

        menu_button_preferences = Gio.Menu()
        menu_button_preferences.append_item(
            Gio.MenuItem.new(_('Configuration'), 'app.set_preferences'))
        menu_button_preferences.append_item(
            Gio.MenuItem.new(_('Download all albums'), 'app.set_preferences'))

        button_preferences = Gtk.MenuButton()
        button_preferences.add(
            Gtk.Image.new_from_gicon(
                Gio.ThemedIcon.new_with_default_fallbacks(
                    'preferences-system-symbolic'),
                Gtk.IconSize.BUTTON))
        button_preferences.set_menu_model(menu_button_preferences)
        hb.pack_end(button_preferences)

        vbox = Gtk.VBox()
        self.add(vbox)
        #
        vbox1 = Gtk.VBox(spacing=0)
        vbox1.set_border_width(0)
        vbox.add(vbox1)
        #
        hbox = Gtk.HBox()
        vbox1.pack_start(hbox, True, True, 0)
        #
        vbox3 = Gtk.VBox()
        hbox.pack_start(vbox3, True, True, 0)
        #
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC,
                                  Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        vbox3.pack_start(scrolledwindow, True, True, 0)
        self.iconview1 = Gtk.IconView()
        self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        scrolledwindow.add(self.iconview1)

        backgroundVBox2 = Gtk.EventBox()
        hbox.pack_start(backgroundVBox2, False, False, 0)
        #
        self.menu_emergente = Gtk.Menu()
        self.menuitem3 = Gtk.MenuItem.new_with_label(_('Information'))
        self.menuitem3.connect('activate', self.on_informacion_activated)
        self.menu_emergente.append(self.menuitem3)
        self.menuitem4 = Gtk.MenuItem.new_with_label(_('Edit'))
        self.menuitem4.connect('activate', self.on_edit_activated)
        self.menu_emergente.append(self.menuitem4)
        self.menuitem5 = Gtk.MenuItem.new_with_label(_('Download'))
        self.menuitem5.connect('activate', self.on_descargar_activated)
        self.menu_emergente.append(self.menuitem5)
        self.menuitem6 = Gtk.MenuItem.new_with_label(_(
            'Copy link to clipboard'))
        self.menuitem6.connect('activate', self.on_menuitem6_activated)
        self.menu_emergente.append(self.menuitem6)
        self.menuitem7 = Gtk.MenuItem.new_with_label(_(
            'Copy thumbnail 72x72 link to clipboard'))
        self.menuitem7.connect('activate', self.on_menuitem7_activated)
        self.menu_emergente.append(self.menuitem7)
        self.menuitem8 = Gtk.MenuItem.new_with_label(_(
            'Copy thumbnail 144x144 link to clipboard'))
        self.menuitem8.connect('activate', self.on_menuitem8_activated)
        self.menu_emergente.append(self.menuitem8)
        self.menuitem9 = Gtk.MenuItem.new_with_label(_(
            'Copy thumbnail 288x288 link to clipboard'))
        self.menuitem9.connect('activate', self.on_menuitem9_activated)
        self.menu_emergente.append(self.menuitem9)
        self.menuitem10 = Gtk.MenuItem.new_with_label(_('Copy link for web'))
        self.menuitem10.connect('activate', self.on_menuitem10_activated)
        self.menu_emergente.append(self.menuitem10)
        self.menuitem11 = Gtk.MenuItem.new_with_label(_('Copy image'))
        self.menuitem11.connect('activate', self.on_menuitem11_activated)
        self.menu_emergente.append(self.menuitem11)
        self.menuitem12 = Gtk.MenuItem.new_with_label(_('Paste image'))
        self.menuitem12.connect('activate', self.on_menuitem12_activated)
        self.menu_emergente.append(self.menuitem12)
        #
        self.menuitem3.set_visible(True)
        self.menuitem4.set_visible(True)
        self.menuitem5.set_visible(True)
        self.menuitem6.set_visible(True)
        self.menuitem7.set_visible(True)
        self.menuitem8.set_visible(True)
        self.menuitem9.set_visible(True)
        self.menuitem10.set_visible(True)
        self.menuitem11.set_visible(True)
        self.menuitem12.set_visible(True)
        #
        self.store = Gtk.ListStore(GdkPixbuf.Pixbuf,
                                   str,
                                   GObject.TYPE_PYOBJECT)
        self.storeimages = Gtk.ListStore(GdkPixbuf.Pixbuf,
                                         str,
                                         GObject.TYPE_PYOBJECT)
        self.iconview1.set_model(self.store)
        self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.iconview1.set_pixbuf_column(0)
        self.iconview1.set_text_column(1)
        self.iconview1.set_item_width(100)
        self.iconview1.set_columns(-1)
        self.iconview1.set_column_spacing(0)
        self.iconview1.set_spacing(0)
        self.iconview1.set_row_spacing(20)
        self.iconview1.set_item_padding(0)
        ################################################################
        self.iconview1.connect('button-press-event',
                               self.on_iconview1_button_press_event)
        self.iconview1.connect('button-release-event',
                               self.on_iconview1_button_release_event)

        self.iconview1.connect('key-release-event',
                               self.on_iconview1_key_release_event)
        # set icon for drag operation
        self.iconview1.connect('drag-begin', self.drag_begin)
        self.iconview1.connect('drag-data-get', self.drag_data_get_data)
        self.iconview1.connect('drag-data-received', self.drag_data_received)
        #
        dnd_list = [Gtk.TargetEntry.new('text/uri-list', 0, 100),
                    Gtk.TargetEntry.new('text/plain', 0, 80)]
        self.iconview1.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                       dnd_list,
                                       Gdk.DragAction.COPY)
        self.iconview1.drag_source_add_uri_targets()
        dnd_list = Gtk.TargetEntry.new("text/uri-list", 0, 0)
        self.iconview1.drag_dest_set(Gtk.DestDefaults.MOTION |
                                     Gtk.DestDefaults.HIGHLIGHT |
                                     Gtk.DestDefaults.DROP,
                                     [dnd_list],
                                     Gdk.DragAction.MOVE)
        self.iconview1.drag_dest_add_uri_targets()
        #
        self.album = None
        self.button_add.set_tooltip_text(_('Add album'))
        self.button_remove.set_tooltip_text(_('Remove album'))
        self.show_all()
        #
        self.set_wait_cursor()
        self.inicia_albums()
        self.set_normal_cursor()

    def drag_begin(self, widget, context):
        if self.album is not None:
            items = self.iconview1.get_selected_items()
            if len(items) > 0:
                selected = self.storeimages.get_iter_from_string(str(items[0]))
                pixbuf = self.storeimages.get_value(selected, 0)
                Gtk.drag_set_icon_pixbuf(context, pixbuf, -2, -2)

    def drag_data_get_data(self, treeview, context, selection, target_id,
                           etime):
        if target_id == 0:
            if self.album is not None:
                items = self.iconview1.get_selected_items()
                files = []
                if len(items) > 0:
                    selected = self.storeimages.get_iter_from_string(
                        str(items[0]))
                    imagen = self.storeimages.get_value(selected, 2)
                    if imagen.params['url'].rfind('/') > -1:
                        ext = imagen.params['url'][-4:]
                        name = self.storeimages.get_value(selected, 1)
                        if name[-4:] != ext:
                            name = name+ext
                        filename = tempfile.mkstemp(suffix='',
                                                    prefix='picapy_tmp',
                                                    dir='/tmp')[1]
                        utils.download_image(imagen.params['url'], filename)
                        if os.path.exists(filename):
                            newname = os.path.join('/tmp', name)
                            os.rename(filename, newname)
                            if os.path.exists(filename):
                                os.remove(filename)
                        location = "file://" + newname
                        files.append(location)
                        selection.set_uris(files)

    def drag_data_received(self, widget, drag_context, x, y, selection_data,
                           info, timestamp):
        if self.album is not None:
            filenames = selection_data.get_uris()
            for_upload = []
            for filename in filenames:
                if len(filename) > 8:
                    filename = urllib.request.url2pathname(filename)
                    filename = filename[7:]
                    mime = mimetypes.guess_type(filename)
                    if os.path.exists(filename):
                        mime = mimetypes.guess_type(filename)[0]
                        if mime in googlepicasaapi.SUPPORTED_MIMES or\
                                mime in googlepicasaapi.CONVERTED_MIMES:
                            for_upload.append(filename)
            if len(for_upload) > 0:
                self.set_wait_cursor()
                progreso = Progreso('Picapy', self, len(for_upload))
                tasker = Tasker(utils.upload_an_image2, for_upload,
                                self.picasa, self.reduce_size, self.max_size,
                                self.reduce_colors, self.album.params['id'])
                progreso.connect('i-want-stop', tasker.stopit)
                tasker.connect('start-one-element',
                               self.uploading,
                               progreso)
                tasker.connect('end-one-element', progreso.increase)
                tasker.connect('end-one-element', self.show_photo)
                tasker.start()
                progreso.run()
                self.set_normal_cursor()
        return True

    def show_photo(self, emiter, photo):
        if photo is not None and self.album is not None:
            if self.album.params['id'] == photo['album_id']:
                self.storeimages.prepend([photo['pixbuf'],
                                          photo['photo_name'],
                                          photo['photo']])

    def load_preferences(self):
        configuration = Configuration()
        self.image_link = configuration.get('image_link')
        self.max_size = configuration.get('max_size')
        self.reduce_size = configuration.get('reduce_size')
        self.reduce_colors = configuration.get('reduce_colors')
        self.image_dir = configuration.get('image_dir')
        self.time_between_images = configuration.get('time_between_images')
        if self.image_dir is None or len(self.image_dir) <= 0 or\
                os.path.exists(self.image_dir) is False:
            self.image_dir = os.getenv('HOME')
        self.first_time = configuration.get('first_time')

    def inicia_images(self):
        modelo = Gtk.ListStore(str)
        self.treeview2.set_model(modelo)
        render = Gtk.CellRendererText()
        columna = Gtk.TreeViewColumn("Imagen", render, text=0)
        self.treeview2.append_column(columna)

    def close_application(self, widget):
        configuration = Configuration()
        configuration.set('image_dir', self.image_dir)
        configuration.save()
        main_thread = threading.currentThread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()
        if self.app is not None:
            self.app.quit()
        exit(0)

    def prepend_album(self, album):
        album_name = album.params['title']
        mfile = os.path.join(comun.IMAGES_DIR,
                             'album_'+album.params['id']+'.png')
        if os.path.exists(mfile):
            os.remove(mfile)
        utils.create_icon(mfile,
                          album.params['thumbnail2'],
                          album.params['access'])
        if os.path.exists(mfile):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
        else:
            pixbuf = PIXBUF_DEFAULT_ALBUM
        self.store.prepend()
        iter = self.store.get_iter_first()
        self.store.set_value(iter, 0, pixbuf)
        self.store.set_value(iter, 1, album_name)
        self.store.set_value(iter, 2, album)

    def inicia_albums(self):
        data_file = os.path.join(comun.IMAGES_DIR, 'album.data')
        data = None
        if os.path.exists(data_file):
            f = codecs.open(data_file, 'r', 'utf-8')
            data = json.loads(f.read())
            f.close()
        self.store.clear()
        self.albums = self.picasa.get_albums()
        if len(self.albums) > 0:
            to_json = {}
            for album in self.albums:
                to_json[album.params['id']] = album.params
            f = open(data_file, 'w')
            f.write(json.dumps(to_json))
            f.close()
            self.set_wait_cursor()
            progreso = Progreso(_('Loading albums')+'...',
                                self,
                                len(self.albums))
            tasker = Tasker(self.get_album_and_create_icon, self.albums,
                            data)
            progreso.connect('i-want-stop', tasker.stopit)
            tasker.connect('start-one-element',
                           self.getting_thumbnail_for_album,
                           progreso)
            tasker.connect('end-one-element', progreso.increase)
            tasker.connect('end-one-element',
                           self.load_thumbnail_for_album)
            tasker.connect('finished', progreso.close)
            tasker.start()
            progreso.run()
            self.set_normal_cursor()

    def get_album_and_create_icon(self, album, data):
        mfile = os.path.join(comun.IMAGES_DIR,
                             'album_'+album.params['id']+'.png')
        if os.path.exists(mfile) is False or data is None or\
                album.params['id'] not in data.keys() or\
                (data[album.params['id']]['etag'] != album.params['etag']):
            utils.create_icon_for_album(album)
        else:
            pixbuf = utils.get_pixbuf_from_url('file://'+mfile)
        return album

    def getting_thumbnail_for_album(self, emiter, album, progreso):
        name = album.params['title']
        if len(name) > 35:
            name = name[:32] + '...'
        label = _('Getting') + ' ' + name
        progreso.set_label(name)

    def load_thumbnail_for_album(self, emiter, album):
        mfile = os.path.join(comun.IMAGES_DIR,
                             'album_'+album.params['id']+'.png')
        if os.path.exists(mfile):
            pixbuf = utils.get_pixbuf_from_url('file://'+mfile)
        else:
            pixbuf = PIXBUF_DEFAULT_ALBUM
        self.store.append([pixbuf, album.params['title'], album])

    def on_edit_activated(self, widget):
        items = self.iconview1.get_selected_items()
        if len(items) > 0:
            if self.album is None:
                selected = self.store.get_iter_from_string(str(items[0]))
                album = self.store.get_value(selected, 2)
                i = EditAlbum(self, album)
                if i.run() == Gtk.ResponseType.ACCEPT:
                    album.params['title'] = i.entry1.get_text()
                    album.params['summary'] = i.entry2.get_text()
                    if i.combobox.get_active() == 0:
                        album.params['rights'] = 'private'
                    elif i.combobox.get_active() == 1:
                        album.params['rights'] = 'protected'
                    else:
                        album.params['rights'] = 'public'
                    updated_album = self.picasa.edit_album(album)
                    if updated_album is not None:
                        album_name = album.params['title']
                        mfile = os.path.join(
                            comun.IMAGES_DIR,
                            'album_'+album.params['id']+'.png')
                        os.remove(mfile)
                        utils.create_icon(mfile,
                                          updated_album.params['thumbnail2'],
                                          updated_album.params['access'])
                        if os.path.exists(mfile):
                            pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
                        else:
                            pixbuf = PIXBUF_DEFAULT_ALBUM
                        self.store.set_value(selected, 0, pixbuf)
                        self.store.set_value(selected, 1,
                                             updated_album.params['title'])
                        self.store.set_value(selected, 2, updated_album)
                i.destroy()
            else:
                selected = self.storeimages.get_iter_from_string(str(items[0]))
                image = self.storeimages.get_value(selected, 2)
                i = EditImage(self, image)
                if i.run() == Gtk.ResponseType.ACCEPT:
                    pixbuf = i.aimage2.get_pixbuf()
                    updated_image = self.picasa.edit_photo_from_pixbuf(
                        self.album.params['id'], image, pixbuf,
                        caption=i.entry2.get_text())
                    if updated_image is not None:
                        mdir = os.path.join(comun.IMAGES_DIR,
                                            'album_' + self.album.params['id'])
                        if not os.path.exists(mdir):
                            os.makedirs(mdir)
                        mfile = os.path.join(
                            mdir, 'photo_'+updated_image.params['id']+'.png')
                        if os.path.exists(mfile):
                            os.remove(mfile)
                        utils.create_icon(mfile,
                                          updated_image.params['thumbnail2'],
                                          updated_image.params['access'])
                        if os.path.exists(mfile):
                            pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
                        else:
                            pixbuf = PIXBUF_DEFAULT_PHOTO
                        self.storeimages.set_value(
                            selected, 0, pixbuf)
                        self.storeimages.set_value(
                            selected, 1, updated_image.params['title'])
                        self.storeimages.set_value(
                            selected, 2, updated_image)
                i.destroy()

    def on_informacion_activated(self, widget):
        items = self.iconview1.get_selected_items()
        if len(items) > 0:
            if self.album is None:
                selected = self.store.get_iter_from_string(str(items[0]))
                i = InformacionAlbum(self, self.store.get_value(selected, 2))
                i.run()
                i.destroy()
            else:
                selected = self.storeimages.get_iter_from_string(str(items[0]))
                i = InformacionImagen(self,
                                      self.storeimages.get_value(selected, 2))
                i.run()
                i.destroy()

    def on_preferences_activate(self, widget):
        p = Preferences(self)
        if p.run() == Gtk.ResponseType.ACCEPT:
            p.save_preferences()
        p.destroy()
        self.load_preferences()
        self.picasa = Picasa(token_file=comun.TOKEN_FILE)
        error = True
        while(error):
            if self.picasa.do_refresh_authorization() is None:
                authorize_url = pi.get_authorize_url()
                ld = LoginDialog(authorize_url)
                ld.run()
                self.picasa.get_authorization(ld.code)
                ld.destroy()
                error = False
                if self.picasa.do_refresh_authorization() is None:
                    md = Gtk.MessageDialog(
                        parent=self,
                        flags=Gtk.DialogFlags.MODAL |
                        Gtk.DialogFlags.DESTROY_WITH_PARENT,
                        type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK_CANCEL,
                        message_format=_('You have to authorize Picapy to use \
it, do you want to authorize?'))
                    if md.run() == Gtk.ResponseType.CANCEL:
                        exit(3)
                else:
                    error = False
            else:
                error = False
        self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
        self.inicia_albums()
        self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))
        self.iconview1.set_model(self.store)
        self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.button_up.set_sensitive(False)
        self.button_slideshow.set_sensitive(False)
        self.album = None
        self.button_add.set_tooltip_text(_('Add album'))
        self.button_remove.set_tooltip_text(_('Remove album'))
        self.set_title('Picapy')

    def on_preview_activated(self, widget):
        if self.album is not None:
            images = []
            items = self.iconview1.get_selected_items()
            if len(items) > 0:
                for item in items:
                    selected = self.storeimages.get_iter_from_string(str(item))
                    image = self.storeimages.get_value(selected, 2)
                    images.append(image)
            else:
                itera = self.storeimages.get_iter_first()
                while(itera):
                    image = self.storeimages.get_value(itera, 2)
                    images.append(image)
                    itera = self.storeimages.iter_next(itera)
            sw = SliderWindow(images, self.time_between_images)

    def on_download_all_activate(self, widget):
        chooser = Gtk.FileChooserDialog(
            title=_('Select where to download all albums'),
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        chooser.set_current_folder(self.image_dir)
        if chooser.run() == Gtk.ResponseType.OK:
            filename = chooser.get_filename()
            self.image_dir = filename
            if self.image_dir is None or len(self.image_dir) <= 0 or\
                    os.path.exists(self.image_dir) is False:
                self.image_dir = os.getenv('HOME')
            chooser.destroy()
            albums = self.picasa.get_albums()
            if len(albums) > 0:
                self.set_wait_cursor()
                progreso = Progreso(_('Downloading all albums...'),
                                    self, len(albums))
                tasker = Tasker(self.download_all_images_from_album, albums,
                                self.image_dir)
                progreso.connect('i-want-stop', tasker.stopit)
                tasker.connect('start-one-element',
                               self.getting_album,
                               progreso)
                tasker.connect('end-one-element', progreso.increase)
                tasker.connect('finished', progreso.close)
                tasker.start()
                progreso.run()
                self.set_normal_cursor()
        chooser.destroy()

    def getting_album(self, emiter, album, progreso):
        print(emiter, album, progreso)
        name = album.params['title']
        if len(name) > 35:
            name = name[:32] + '...'
        label = _('Getting') + ' ' + name
        progreso.set_label(name)

    def download_all_images_from_album(self, album, folder):
        print('*******************')
        print(folder)
        folder = os.path.join(folder, album.params['id'])
        print(folder)
        print('*******************')
        if not os.path.exists(folder):
            os.mkdir(folder)
        photos = self.picasa.get_photos(album.params['id'])
        utils.download_all_images(folder, photos)
        return album

    def set_wait_cursor(self):
        self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
        while Gtk.events_pending():
            Gtk.main_iteration()

    def set_normal_cursor(self):
        self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))
        while Gtk.events_pending():
            Gtk.main_iteration()

    def on_descargar_activated(self, widget):
        items = self.iconview1.get_selected_items()
        if len(items) > 0:
            if self.album is None:
                chooser = Gtk.FileChooserDialog(
                    title=_('Select where to download the album'),
                    parent=self,
                    action=Gtk.FileChooserAction.SELECT_FOLDER,
                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
                chooser.set_current_folder(self.image_dir)
                if chooser.run() == Gtk.ResponseType.OK:
                    filename = chooser.get_filename()
                    self.image_dir = os.path.dirname(filename)
                    if self.image_dir is None or len(self.image_dir) <= 0 or\
                            not os.path.exists(self.image_dir):
                        self.image_dir = os.getenv('HOME')
                    chooser.destroy()
                    if len(items) > 0:
                        self.set_wait_cursor()
                        albums = []
                        for item in items:
                            itera = self.store.get_iter_from_string(str(item))
                            album = self.store.get_value(itera, 2)
                            albums.append(album)
                        progreso = Progreso(_('Downloading albums...'),
                                            self, len(albums))
                        tasker = Tasker(self.download_all_images_from_album,
                                        albums, self.image_dir)
                        progreso.connect('i-want-stop', tasker.stopit)
                        tasker.connect('start-one-element',
                                       self.getting_album,
                                       progreso)
                        tasker.connect('end-one-element', progreso.increase)
                        tasker.connect('finished', progreso.close)
                        tasker.start()
                        progreso.run()
                        self.set_normal_cursor()
                chooser.destroy()
            else:
                chooser = Gtk.FileChooserDialog(
                    title=_('Select where download images'),
                    parent=self,
                    action=Gtk.FileChooserAction.SELECT_FOLDER,
                    buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
                if chooser.run() == Gtk.ResponseType.OK:
                    dirname = chooser.get_filename()
                    self.set_wait_cursor()
                    photos = []
                    for item in items:
                        itera = self.storeimages.get_iter_from_string(
                            str(item))
                        photo = self.storeimages.get_value(itera, 2)
                        photos.append(photo)
                    progreso = Progreso(_('Downloading images...'),
                                        self, len(photos))
                    tasker = Tasker(utils.download_a_photo, photos,
                                    dirname)
                    progreso.connect('i-want-stop', tasker.stopit)
                    tasker.connect('start-one-element',
                                   self.getting_photo,
                                   progreso)
                    tasker.connect('end-one-element', progreso.increase)
                    tasker.connect('finished', progreso.close)
                    tasker.start()
                    progreso.run()
                self.set_normal_cursor()
                chooser.destroy()

    def getting_photo(self, emiter, photo, progreso):
        # print(emiter, photo, progreso)
        print(emiter, progreso)
        name = photo.params['title']
        if len(name) > 35:
            name = name[:32] + '...'
        label = _('Getting') + ' ' + name
        progreso.set_label(name)

    def on_menuitem6_activated(self, widget):
        items = self.iconview1.get_selected_items()
        if len(items) > 0:
            selected = self.storeimages.get_iter_from_string(str(items[0]))
            imagen = self.storeimages.get_value(selected, 2)
            text = imagen.params['url']
            atom = Gdk.atom_intern('CLIPBOARD', True)
            clipboard = self.iconview1.get_clipboard(atom)
            clipboard.set_text(text, -1)

    def on_menuitem7_activated(self, widget):
        items = self.iconview1.get_selected_items()
        if len(items) > 0:
            selected = self.storeimages.get_iter_from_string(str(items[0]))
            imagen = self.storeimages.get_value(selected, 2)
            text = imagen.thumbnails[0]['url']
            atom = Gdk.atom_intern('CLIPBOARD', True)
            clipboard = self.iconview1.get_clipboard(atom)
            clipboard.set_text(text, -1)

    def on_menuitem8_activated(self, ):
        items = self.iconview1.get_selected_items()
        if len(items) > 0:
            selected = self.storeimages.get_iter_from_string(str(items[0]))
            imagen = self.storeimages.get_value(selected, 2)
            text = imagen.thumbnails[1]['url']
            atom = Gdk.atom_intern('CLIPBOARD', True)
            clipboard = self.iconview1.get_clipboard(atom)
            clipboard.set_text(text, -1)

    def on_menuitem9_activated(self, widget):
        items = self.iconview1.get_selected_items()
        if len(items) > 0:
            selected = self.storeimages.get_iter_from_string(str(items[0]))
            imagen = self.storeimages.get_value(selected, 2)
            text = imagen.thumbnails[2]['url']
            atom = Gdk.atom_intern('CLIPBOARD', True)
            clipboard = self.iconview1.get_clipboard(atom)
            clipboard.set_image(text, -1)

    def on_menuitem10_activated(self, widget):
        items = self.iconview1.get_selected_items()
        if len(items) > 0:
            selected = self.storeimages.get_iter_from_string(str(items[0]))
            imagen = self.storeimages.get_value(selected, 2)
            text = self.image_link
            text = text.replace('%TITLE%', imagen.params['title'])
            text = text.replace('%URL%', imagen.params['url'])
            text = text.replace('%URL72%', imagen.thumbnails[0]['url'])
            text = text.replace('%URL144%', imagen.thumbnails[1]['url'])
            text = text.replace('%URL288%', imagen.thumbnails[2]['url'])
            atom = Gdk.atom_intern('CLIPBOARD', True)
            clipboard = self.iconview1.get_clipboard(atom)
            clipboard.set_text(text, -1)

    def on_menuitem11_activated(self, widget):
        items = self.iconview1.get_selected_items()
        if len(items) > 0:
            selected = self.storeimages.get_iter_from_string(str(items[0]))
            imagen = self.storeimages.get_value(selected, 2)
            pixbuf = utils.get_pixbuf_from_url(imagen.params['url'])
            atom = Gdk.atom_intern('CLIPBOARD', True)
            clipboard = self.iconview1.get_clipboard(atom)
            clipboard.set_image(pixbuf)
            clipboard.store()

    def on_menuitem12_activated(self, widget):
        if self.album is not None:
            atom = Gdk.atom_intern('CLIPBOARD', True)
            clipboard = Gtk.Clipboard.get(atom)
            pixbuf = clipboard.wait_for_image()
            if pixbuf is not None:
                ia = PasteImage(self, None)
                if ia.run() == Gtk.ResponseType.ACCEPT:
                    titulo = ia.entry1.get_text()
                    sumario = ia.entry2.get_text()
                    ia.destroy()
                    if titulo is not None and len(titulo) > 0:
                        photo = self.picasa.add_image_from_pixbuf(
                            self.album.params['id'],
                            pixbuf,
                            titulo,
                            sumario,
                            self.reduce_size,
                            self.max_size,
                            self.reduce_colors)
                        mdir = os.path.join(
                            comun.IMAGES_DIR, 'album_'+self.album.params['id'])
                        if not os.path.exists(mdir):
                            os.makedirs(mdir)
                        mfile = os.path.join(
                            mdir, 'photo_'+photo.params['id']+'.png')
                        utils.create_icon(
                            mfile,
                            photo.params['thumbnail2'],
                            photo.params['access'])
                        if os.path.exists(mfile):
                            pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
                        else:
                            pixbuf = PIXBUF_DEFAULT_PHOTO
                        self.storeimages.prepend([pixbuf, titulo, photo])
                ia.destroy()

    def on_iconview1_button_press_event(self, widget, event):
        #
        # if event.button==1 and event.type==Gdk.BUTTON_PRESS:
        #
        # Gdk.EventType.2BUTTON_PRESS is not working in python because
        # it starts with number so use Gdk.EventType(value = 5) to construct
        # 2BUTTON_PRESS event type
        if event.button == 1 and event.type == Gdk.EventType(value=5):
            if self.album is None:
                items = self.iconview1.get_selected_items()
                if len(items) > 0:
                    selected = self.store.get_iter_from_string(str(items[0]))
                    self.set_wait_cursor()
                    while Gtk.events_pending():
                        Gtk.main_iteration()
                    self.load_images_from_picasa_album(
                        self.store.get_value(selected, 2))
                    self.set_normal_cursor()
            else:
                items = self.iconview1.get_selected_items()
                if len(items) > 0:
                    selected = self.storeimages.get_iter_from_string(
                        str(items[0]))
                    image = self.storeimages.get_value(selected, 2)
                    v = VerImagen(self, image)
                    v.run()
                    v.destroy()

    def on_iconview1_button_release_event(self, widget, event):
        if event.button == 3:
            items = self.iconview1.get_selected_items()
            if len(items) > 0:
                if self.album is None:
                    self.menuitem4.set_sensitive(True)
                    self.menuitem5.set_sensitive(True)
                    self.menuitem6.set_sensitive(False)
                    self.menuitem7.set_sensitive(False)
                    self.menuitem8.set_sensitive(False)
                    self.menuitem9.set_sensitive(False)
                    self.menuitem10.set_sensitive(False)
                    self.menuitem11.set_sensitive(False)
                    self.menuitem12.set_sensitive(False)
                else:
                    self.menuitem3.set_sensitive(True)
                    self.menuitem4.set_sensitive(True)
                    self.menuitem5.set_sensitive(True)
                    self.menuitem6.set_sensitive(True)
                    self.menuitem7.set_sensitive(True)
                    self.menuitem8.set_sensitive(True)
                    self.menuitem9.set_sensitive(True)
                    self.menuitem10.set_sensitive(True)
                    self.menuitem11.set_sensitive(True)
                    self.menuitem12.set_sensitive(True)
                self.menu_emergente.popup(None, None, None, None, 0, 0)
            elif self.album is not None:
                self.menuitem3.set_sensitive(False)
                self.menuitem4.set_sensitive(False)
                self.menuitem5.set_sensitive(False)
                self.menuitem6.set_sensitive(False)
                self.menuitem7.set_sensitive(False)
                self.menuitem8.set_sensitive(False)
                self.menuitem9.set_sensitive(False)
                self.menuitem10.set_sensitive(False)
                self.menuitem11.set_sensitive(False)
                self.menuitem12.set_sensitive(True)
                self.menu_emergente.popup(None, None, None, None, 0, 0)

    def on_iconview1_key_release_event(self, widget, event):
        values = []
        values.append(Gdk.keyval_from_name('Return'))
        values.append(Gdk.keyval_from_name('KP_Enter'))
        values.append(Gdk.keyval_from_name('space'))
        if event.keyval in values:
            if self.album is None:
                items = self.iconview1.get_selected_items()
                if len(items) > 0:
                    selected = self.store.get_iter_from_string(str(items[0]))
                    self.set_wait_cursor()
                    self.load_images_from_picasa_album(
                        self.store.get_value(selected, 2))
                    self.set_normal_cursor()
            else:
                items = self.iconview1.get_selected_items()
                if len(items) > 0:
                    selected = self.storeimages.get_iter_from_string(
                        str(items[0]))
                    image = self.storeimages.get_value(selected, 2)
                    v = VerImagen(self, image)
                    v.run()
                    v.destroy()
        elif event.keyval == Gdk.keyval_from_name('BackSpace'):
            if self.album is not None:
                self.iconview1.set_model(self.store)
                self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
                self.button_up.set_sensitive(False)
                self.button_slideshow.set_sensitive(False)
                self.album = None
                self.set_title('Picapy')
        elif event.keyval == Gdk.keyval_from_name('Delete'):
            self.on_remove_button_clicked(None)

    def load_images_from_picasa_album(self, album):
        self.set_title('Picapy | ' + album.params['title'])
        mdir = os.path.join(comun.IMAGES_DIR, 'album_'+album.params['id'])
        if not os.path.exists(mdir):
            os.makedirs(mdir)
        data_file = os.path.join(mdir, 'photo.data')
        data = None
        if os.path.exists(data_file):
            f = codecs.open(data_file, 'r', 'utf-8')
            data = json.loads(f.read())
            f.close()
        photos = self.picasa.get_photos(album.params['id'])
        self.storeimages.clear()
        self.iconview1.set_model(self.storeimages)
        self.iconview1.show()
        self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        if len(photos) > 0:
            results = []
            to_json = {}
            photos.sort()
            for photo in photos:
                to_json[photo.params['id']] = photo.params
            mdir = os.path.join(comun.IMAGES_DIR, 'album_'+album.params['id'])
            if not os.path.exists(mdir):
                os.makedirs(mdir)
            f = open(data_file, 'w')
            f.write(json.dumps(to_json))
            f.close()

            self.set_wait_cursor()
            progreso = Progreso(_('Loading images for album'),
                                self, len(photos))
            tasker = Tasker(self.get_photo_and_create_icon, photos,
                            album, data)
            progreso.connect('i-want-stop', tasker.stopit)
            tasker.connect('start-one-element',
                           self.getting_thumbnail,
                           progreso)
            tasker.connect('end-one-element', progreso.increase)
            tasker.connect('end-one-element', self.load_thumbnail, mdir)
            tasker.connect('finished', progreso.close)
            tasker.start()
            progreso.run()
            self.set_normal_cursor()

        self.album = album
        self.button_add.set_tooltip_text(_('Add image'))
        self.button_remove.set_tooltip_text(_('Remove image'))
        self.button_up.set_sensitive(True)
        self.button_slideshow.set_sensitive(True)
        self.button_download.set_sensitive(True)

    def getting_thumbnail(self, emiter, photo, progreso):
        print(emiter, photo, progreso)
        name = photo.params['title']
        if len(name) > 35:
            name = name[:32] + '...'
        label = _('Getting') + ' ' + name
        progreso.set_label(name)

    def get_photo_and_create_icon(self, photo, album, data):
        mdir = os.path.join(comun.IMAGES_DIR, 'album_'+album.params['id'])
        if not os.path.exists(mdir):
            os.makedirs(mdir)
        mfile = os.path.join(mdir, 'photo_'+photo.params['id']+'.png')
        if os.path.exists(mfile) is False:
            utils.create_icon_for_photo(album.params['id'], photo)
        elif data is not None and (photo.params['id'] not in data.keys()) or\
                (data[photo.params['id']]['etag'] != photo.params['etag']):
            utils.create_icon_for_photo(album.params['id'], photo)
        return photo

    def load_thumbnail(self, emiter, photo, mdir):
        print(emiter, photo, mdir)
        photo_name = photo.params['title']
        mfile = os.path.join(mdir, 'photo_'+photo.params['id']+'.png')
        if os.path.exists(mfile):
            pixbuf = utils.get_pixbuf_from_url('file://'+mfile)
        else:
            pixbuf = PIXBUF_DEFAULT_PHOTO
        self.storeimages.append([pixbuf, photo.params['title'], photo])

    def on_button1_clicked(self, widget):
        self.iconview1.set_model(self.store)
        self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.button_up.set_sensitive(False)
        self.button_slideshow.set_sensitive(False)
        self.album = None
        self.button_add.set_tooltip_text(_('Add album'))
        self.button_remove.set_tooltip_text(_('Remove album'))
        self.set_title('Picapy')

    def on_remove_button_clicked(self, widget):
        if self.album is None:
            items = self.iconview1.get_selected_items()
            if len(items) > 0:
                if len(items) > 1:
                    msg = _('Do you want to delete %s folders?') % str(len(
                        items))
                    msg2 = _('Deleting folders...')
                else:
                    msg = _('Do you want to delete this folder?')
                    msg2 = _('Deleting folder...')
                md = Gtk.MessageDialog(self,
                                       Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                       Gtk.MessageType.QUESTION,
                                       Gtk.ButtonsType.OK_CANCEL, msg)
                respuesta = md.run()
                if respuesta == Gtk.ResponseType.OK:
                    md.destroy()
                    p = Progreso(msg2, self, len(items))
                    for item in items:
                        itera = self.store.get_iter_from_string(str(item))
                        selected = self.store.get_value(itera, 2)
                        if self.picasa.delete_album(selected):
                            self.store.remove(itera)
                        p.increase()
                    p.destroy()
                else:
                    md.destroy()
        else:
            items = self.iconview1.get_selected_items()
            if len(items) > 0:
                if len(items) > 1:
                    msg = _('Do you want to delete %s images?') % str(len(
                        items))
                    msg2 = _('Deleting images...')
                else:
                    msg = _('Do you want to delete this image?')
                    msg2 = _('Deleting image...')
                md = Gtk.MessageDialog(self,
                                       Gtk.DialogFlags.DESTROY_WITH_PARENT,
                                       Gtk.MessageType.QUESTION,
                                       Gtk.ButtonsType.OK_CANCEL, msg)
                respuesta = md.run()
                if respuesta == Gtk.ResponseType.OK:
                    md.destroy()
                    self.set_wait_cursor()
                    progreso = Progreso(msg2, self, len(items))
                    iters = []
                    for item in items:
                        iters.append(self.storeimages.get_iter(item))
                    tasker = Tasker(utils.remove_an_image, iters, self.picasa,
                                    self.storeimages, self.album)
                    progreso.connect('i-want-stop', tasker.stopit)
                    tasker.connect('start-one-element',
                                   self.removing,
                                   progreso)
                    tasker.connect('end-one-element', progreso.increase)
                    tasker.connect('end-one-element',
                                   self.remove_photo,
                                   self.album)
                    tasker.connect('finished', progreso.close)
                    tasker.start()
                    progreso.run()
                    self.set_normal_cursor()
                else:
                    md.destroy()

    def removing(self, emiter, iter, progreso):
        print(emiter, iter, progreso)
        if iter is not None:
            name = self.storeimages.get_value(iter, 1)
            if len(name) > 35:
                name = name[:32] + '...'
            label = _('Removing') + ' ' + name
            progreso.set_label(label)

    def remove_photo(self, emiter, iter, album):
        if iter is not None and self.album is not None:
            if self.album.params['id'] == album.params['id']:
                self.storeimages.remove(iter)

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

    def on_button2_clicked(self, widget):
        if self.album is None:
            n = NuevoAlbum(self)
            if n.run() == Gtk.ResponseType.ACCEPT:
                title = n.get_album()
                summary = n.get_commentary()
                access = n.get_access()
                if len(title) > 0:
                    album = self.picasa.add_album(title,
                                                  summary=summary,
                                                  access=access)
                    if album is not None:
                        self.prepend_album(album)
            n.destroy()
        else:
            dialog = Gtk.FileChooserDialog(_(
                'Select one or more images to upload to Picasa Web'),
                self,
                Gtk.FileChooserAction.OPEN,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
            dialog.set_default_response(Gtk.ResponseType.OK)
            dialog.set_select_multiple(True)
            dialog.set_current_folder(self.image_dir)
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
                filenames = dialog.get_filenames()
                self.image_dir = os.path.dirname(filenames[0])
                if self.image_dir is None or len(self.image_dir) <= 0 or\
                        not os.path.exists(self.image_dir):
                    self.image_dir = os.getenv('HOME')
                dialog.destroy()
                if len(filenames) > 0:
                    self.set_wait_cursor()
                    progreso = Progreso('Picapy', self, len(filenames))
                    tasker = Tasker(utils.upload_an_image2, filenames,
                                    self.picasa, self.reduce_size,
                                    self.max_size,
                                    self.reduce_colors,
                                    self.album.params['id'])
                    progreso.connect('i-want-stop', tasker.stopit)
                    tasker.connect('start-one-element',
                                   self.uploading,
                                   progreso)
                    tasker.connect('end-one-element', progreso.increase)
                    tasker.connect('end-one-element', self.show_photo)
                    tasker.connect('finished', progreso.close)
                    tasker.start()
                    progreso.run()
                    self.set_normal_cursor()
            dialog.destroy()

    def uploading(self, emiter, filename, progreso):
        print(emiter, filename, progreso)
        filename = os.path.basename(filename)
        if len(filename) > 35:
            filename = '...' + filename[:-32]
        label = _('Uploading') + ' ' + filename
        progreso.set_label(label)


if __name__ == '__main__':
    v = MainWindow(None)
    Gtk.main()

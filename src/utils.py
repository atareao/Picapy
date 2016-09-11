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

import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import urllib.request
import os
from os import path
import time
import re
import html.entities
import cairo


def download_image(url_image, filename):
    opener1 = urllib.request.build_opener()
    page1 = opener1.open(url_image)
    my_picture = page1.read()
    #
    fout = open(filename, "wb")
    fout.write(my_picture)
    fout.close()


def download_image_to_pixbuf(url_image):
    opener1 = urllib.request.build_opener()
    page1 = opener1.open(url_image)
    data = page1.read()
    loader = GdkPixbuf.PixbufLoader()
    loader.write(data)
    loader.close()
    pixbuf = loader.get_pixbuf()
    return pixbuf


def wait(time_lapse):
    time_start = time.time()
    time_end = (time_start + time_lapse)
    while time_end > time.time():
        while Gtk.events_pending():
            Gtk.main_iteration()


def get_surface_from_pixbuf(pixbuf):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                 pixbuf.get_width(),
                                 pixbuf.get_height())
    context = cairo.Context(surface)
    Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
    context.paint()
    return surface


def get_pixbuf_from_url(url):
    try:
        opener1 = urllib.request.build_opener()
        page1 = opener1.open(url)
        data = page1.read()
        loader = GdkPixbuf.PixbufLoader()
        loader.write(data)
        loader.close()
        pixbuf = loader.get_pixbuf()
        return pixbuf
    except Exception as e:
        print(e)
        logging.info(e)
    return PIXBUF_DEFAULT_ALBUM


def create_icon(output, url, access):
    pixbuf_main = get_pixbuf_from_url(url)
    status_icon_file = os.path.join(comun.IMGDIR, access+'.svg')
    logging.info(access)
    pixbuf_icon = GdkPixbuf.Pixbuf.new_from_file(status_icon_file)
    if pixbuf_main is not None and pixbuf_icon is not None:
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
        context = cairo.Context(surface)
        surface_main = get_surface_from_pixbuf(pixbuf_main)
        mw, mh = surface_main.get_width(), surface_main.get_height()
        zoom = 1
        if mw > 100 or mh > 100:
            if mw > mh:
                zoom = mh/mw
                mh = int(mh/mw*100)
                mw = 100
            else:
                zoom = mw/mh
                mw = int(mw/mh*100)
                mh = 100
        context.save()
        context.translate((100-mw)/2, (100-mh)/2)
        context.scale(zoom, zoom)
        context.set_source_surface(surface_main)
        context.paint()
        context.restore()
        surface_icon = get_surface_from_pixbuf(pixbuf_icon)
        iw, ih = surface_icon.get_width(), surface_icon.get_height()
        context.save()
        context.translate(100-iw, 100-ih)
        context.set_source_surface(surface_icon)
        context.paint()
        context.restore()
        surface.write_to_png(output)


def create_icon_for_album(album):
    mfile = os.path.join(comun.IMAGES_DIR, 'album_'+album.params['id']+'.png')
    create_icon(mfile, album.params['thumbnail2'], album.params['rights'])


def create_icon_for_photo(album_id, photo):
    mdir = os.path.join(comun.IMAGES_DIR, 'album_'+album_id)
    if not os.path.exists(mdir):
        os.makedirs(mdir)
    mfile = os.path.join(mdir, 'photo_'+photo.params['id']+'.png')
    create_icon(mfile, photo.params['thumbnail2'], photo.params['access'])


def get_photo(album_id, photo, force=False):
    photo_name = photo.params['title']
    mdir = os.path.join(comun.IMAGES_DIR, 'album_'+album_id)
    if not os.path.exists(mdir):
        os.makedirs(mdir)
    mfile = os.path.join(mdir, 'photo_'+photo.params['id']+'.png')
    if not force and os.path.exists(mfile):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
    else:
        create_icon(mfile, photo.params['thumbnail2'], photo.params['rights'])
    ans = {'index': photo.params['edited'],
           'pixbuf': mfile,
           'photo_name': photo_name,
           'photo': photo}
    return ans


def get_album(album, force=False):
    try:
        album_name = album.params['title']
        if album.params['thumbnail2'] is not None:
            mfile = os.path.join(comun.IMAGES_DIR,
                                 'album_'+album.params['id'] + '.png')
            if not force and os.path.exists(mfile):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
            else:
                create_icon(mfile,
                            album.params['thumbnail2'],
                            album.params['rights'])
        ans = {'index': album.params['edited'],
               'pixbuf': mfile,
               'album_name': album_name,
               'album': album}
        return ans
    except Exception as e:
        logging.info(e)
    return None


def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return chr(int(text[3:-1], 16))
                else:
                    return chr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = chr(html.entities.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text
    return re.sub("&#?\w+;", fixup, text)


def add2menu(menu, text=None, icon=None, conector_event=None,
             conector_action=None):
    if text is not None:
        menu_item = Gtk.ImageMenuItem.new_with_label(text)
        if icon:
            image = Gtk.Image.new_from_stock(icon, Gtk.IconSize.MENU)
            menu_item.set_image(image)
            menu_item.set_always_show_image(True)
    else:
        if icon is None:
            menu_item = Gtk.SeparatorMenuItem()
        else:
            menu_item = Gtk.ImageMenuItem.new_from_stock(icon, None)
            menu_item.set_always_show_image(True)
    if conector_event is not None and conector_action is not None:
        menu_item.connect(conector_event, conector_action)
    menu_item.show()
    menu.append(menu_item)
    return menu_item


def resize_image(filename, size, colors):
    image = Image.open(filename)
    w, h = image.size
    if size is True:
        if w > h:
            zw = w / 4920
            zh = h / 3264
        else:
            zw = w / 3264
            zh = h / 4920
        if zw > zh:
            z = zw
        else:
            z = zh
        w = w / z
        h = h / z
        image = image.resize([w, h], Image.ANTIALIAS)
    if colors is True:
        image = image.convert('P', palette=Image.WEB)
    image.save(filename)


def download_an_album(album, force):
    album_name = album.params['title']
    mfile = os.path.join(comun.IMAGES_DIR, 'album_'+album.params['id']+'.png')
    if force or not os.path.exists(mfile):
        if os.path.exists(mfile):
            os.remove(mfile)
        create_icon(mfile, album.params['thumbnail2'], album.params['access'])
    if os.path.exists(mfile):
        pixbuf = get_pixbuf_from_url('file://'+mfile)
    else:
        pixbuf = PIXBUF_DEFAULT_ALBUM
    ans = {'index': album.params['edited'],
           'pixbuf': pixbuf,
           'album_name': album_name,
           'album': album}
    return ans


def download_all_images(adir, aphoto):
    filename = os.path.join(adir, aphoto.params['title']+'png')
    opener1 = urllib.request.build_opener()
    try:
        page1 = opener1.open(aphoto.params['url'])
        my_picture = page1.read()
        fout = open(filename, "wb")
        fout.write(my_picture)
        fout.close()
    except:
        return False
    return True


def download_an_image(album_id, photo, force):
    pixbuf = PIXBUF_DEFAULT_PHOTO
    photo_name = photo.params['title']
    mdir = os.path.join(comun.IMAGES_DIR, 'album_'+album_id)
    if not os.path.exists(mdir):
        os.makedirs(mdir)
    mfile = os.path.join(mdir, 'photo_'+photo.params['id']+'.png')
    if force or not os.path.exists(mfile):
        if os.path.exists(mfile):
            os.remove(mfile)
        create_icon(mfile, photo.params['thumbnail2'], photo.params['access'])
    if os.path.exists(mfile):
        pixbuf = get_pixbuf_from_url('file://'+mfile)
    else:
        pixbuf = PIXBUF_DEFAULT_PHOTO
    ans = {'index': photo.params['edited'],
           'pixbuf': pixbuf,
           'photo_name': photo_name,
           'photo': photo}
    return pixbuf, ans


def upload_an_image(picasa, reduce_size, size, colors, album_id, filename,
                    title, comment):
    uploaded = False
    while not uploaded:
        try:
            photo = picasa.add_image(album_id, filename, title, comment,
                                     reduce_size, size, colors)
            uploaded = True
        except Exception as e:
            logging.info(e)
            wait(await)
            await += .1
    if photo is not None:
        photo_name = photo.params['title']
        mdir = os.path.join(comun.IMAGES_DIR, 'album_'+album_id)
        if not os.path.exists(mdir):
            os.makedirs(mdir)
        mfile = os.path.join(mdir, 'photo_'+photo.params['id']+'.png')
        if os.path.exists(mfile):
            os.remove(mfile)
        create_icon(mfile, photo.params['thumbnail2'], photo.params['access'])
        if os.path.exists(mfile):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
        else:
            pixbuf = PIXBUF_DEFAULT_PHOTO
            ans = {'index': photo.params['edited'],
                   'pixbuf': pixbuf,
                   'photo_name': photo_name,
                   'photo': photo}
        return ans
    return None

#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
__author__="Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>"
__date__ ="$24-abr-2010 12:34:44$"
#
#
# Copyright (C) 2010, 2011, 2012 Lorenzo Carbonell
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
#
#
#

import sys
import gi  
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject
import time
import urllib.request, urllib.parse, urllib.error
import configparser
import os
from os import path
import threading
import webbrowser
import time
import concurrent.futures
#
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
import re, html.entities

import mimetypes
import json
import codecs
import cairo
import queue

import logging

TARGET_TYPE_TEXT = 80
TARGET_TYPE_PIXMAP = 81

NUM_THREADS = 10

PIXBUF_DEFAULT_ALBUM = GdkPixbuf.Pixbuf.new_from_file(comun.DEFAULT_ALBUM)
PIXBUF_DEFAULT_PHOTO = GdkPixbuf.Pixbuf.new_from_file(comun.DEFAULT_PHOTO)

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

########################################################################
#############################FUNCTIONS##################################
########################################################################
def download_image(url_image,filename):		
	opener1 =  	urllib.request.build_opener()
	page1 = opener1.open(url_image)
	my_picture = page1.read()
	#
	fout = open(filename, "wb")
	fout.write(my_picture)
	fout.close()
	
def download_image_to_pixbuf(url_image):
	opener1 =  	urllib.request.build_opener()
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
	surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(),pixbuf.get_height())
	context = cairo.Context(surface)
	Gdk.cairo_set_source_pixbuf(context, pixbuf,0,0)
	context.paint()
	return surface
	
def get_pixbuf_from_url(url):
	try:
		opener1 =  	urllib.request.build_opener()
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

def create_icon(output,url,access):
	pixbuf_main = get_pixbuf_from_url(url)
	status_icon_file = os.path.join(comun.IMGDIR,access+'.svg')
	logging.info(access)
	pixbuf_icon = GdkPixbuf.Pixbuf.new_from_file(status_icon_file)
	if pixbuf_main is not None and pixbuf_icon is not None:
		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100,100)
		context = cairo.Context(surface)		
		surface_main = get_surface_from_pixbuf(pixbuf_main)
		mw,mh = surface_main.get_width(),surface_main.get_height()
		zoom = 1
		if mw > 100 or mh >100:
			if mw > mh:	
				zoom = mh/mw
				mh = int(mh/mw*100)
				mw = 100
			else:
				zoom = mw/mh
				mw = int(mw/mh*100)
				mh = 100
		context.save()
		context.translate((100-mw)/2,(100-mh)/2)
		context.scale(zoom,zoom)
		context.set_source_surface(surface_main)
		context.paint()
		context.restore()
		surface_icon = get_surface_from_pixbuf(pixbuf_icon)
		iw,ih = surface_icon.get_width(),surface_icon.get_height()
		context.save()
		context.translate(100-iw,100-ih)
		context.set_source_surface(surface_icon)
		context.paint()
		context.restore()			
		surface.write_to_png(output)


def create_icon_for_album(album):
	mfile = os.path.join(comun.IMAGES_DIR,'album_'+album.params['id']+'.png')
	create_icon(mfile,album.params['thumbnail2'],album.params['rights'])
	
def create_icon_for_photo(album_id,photo):
	mdir = os.path.join(comun.IMAGES_DIR,'album_'+album_id)
	if not os.path.exists(mdir):
		os.makedirs(mdir)
	mfile = os.path.join(mdir,'photo_'+photo.params['id']+'.png')
	create_icon(mfile,photo.params['thumbnail2'],photo.params['access'])

def get_photo(album_id,photo,force=False):
	photo_name=photo.params['title']
	mdir = os.path.join(comun.IMAGES_DIR,'album_'+album_id)
	if not os.path.exists(mdir):
		os.makedirs(mdir)
	mfile = os.path.join(mdir,'photo_'+photo.params['id']+'.png')
	if not force and os.path.exists(mfile):
		pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
	else:
		create_icon(mfile,photo.params['thumbnail2'],photo.params['rights'])
	ans = {'index':photo.params['edited'],'pixbuf':mfile,'photo_name':photo_name,'photo':photo}
	return ans	

def get_album(album,force=False):
	try:
		album_name=album.params['title']
		if album.params['thumbnail2'] is not None:
			mfile = os.path.join(comun.IMAGES_DIR,'album_'+album.params['id']+'.png')
			
			if not force and os.path.exists(mfile):
				pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
			else:
				create_icon(mfile,album.params['thumbnail2'],album.params['rights'])
		ans = {'index':album.params['edited'],'pixbuf':mfile,'album_name':album_name,'album':album}
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
		return text # leave as is
	return re.sub("&#?\w+;", fixup, text)

def add2menu(menu, text = None, icon = None, conector_event = None, conector_action = None):
	if text != None:
		menu_item = Gtk.ImageMenuItem.new_with_label(text)
		if icon:
			image = Gtk.Image.new_from_stock(icon, Gtk.IconSize.MENU)
			menu_item.set_image(image)
			menu_item.set_always_show_image(True)
	else:
		if icon == None:
			menu_item = Gtk.SeparatorMenuItem()
		else:
			menu_item = Gtk.ImageMenuItem.new_from_stock(icon, None)
			menu_item.set_always_show_image(True)
	if conector_event != None and conector_action != None:				
		menu_item.connect(conector_event,conector_action)
	menu_item.show()
	menu.append(menu_item)
	return menu_item
	
def resize_image(filename,size,colors):
	image = Image.open(filename)
	w,h = image.size
	if size == True and (w>800 or h>800):
		maximo = 800
		if w > h:
			h = h * maximo/w
			w = maximo
		else:
			w = w * maximo/h
			h = maximo
		image = image.resize([w,h],Image.ANTIALIAS)
	if colors == True:
		image = image.convert('P',palette = Image.WEB)
	image.save(filename)
	
########################################################################
#############################CLASSES####################################
########################################################################

def download_an_album(album,force):
	album_name=album.params['title']
	mfile = os.path.join(comun.IMAGES_DIR,'album_'+album.params['id']+'.png')
	if force or not os.path.exists(mfile):
		if os.path.exists(mfile):
			os.remove(mfile)
		create_icon(mfile,album.params['thumbnail2'],album.params['access'])
	if os.path.exists(mfile):
		#pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
		pixbuf = get_pixbuf_from_url('file://'+mfile)
	else:
		pixbuf = PIXBUF_DEFAULT_ALBUM
	ans = {'index':album.params['edited'],'pixbuf':pixbuf,'album_name':album_name,'album':album}	
	return ans
	
def download_all_images(adir,aphoto):
	filename = os.path.join(adir,aphoto.params['title']+'png')
	opener1 =  	urllib.request.build_opener()
	try:
		page1 = opener1.open(aphoto.params['url'])
		my_picture = page1.read()
		fout = open(filename, "wb")
		fout.write(my_picture)
		fout.close()
	except:
		return False
	return True
	
def download_an_image(album_id,photo,force):
	pixbuf = PIXBUF_DEFAULT_PHOTO
	photo_name=photo.params['title']
	mdir = os.path.join(comun.IMAGES_DIR,'album_'+album_id)
	if not os.path.exists(mdir):
		os.makedirs(mdir)
	mfile = os.path.join(mdir,'photo_'+photo.params['id']+'.png')
	if force or not os.path.exists(mfile):
		if os.path.exists(mfile):
			os.remove(mfile)
		create_icon(mfile,photo.params['thumbnail2'],photo.params['access'])
	if os.path.exists(mfile):
		pixbuf = get_pixbuf_from_url('file://'+mfile)
		#pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
	else:
		pixbuf = PIXBUF_DEFAULT_PHOTO
	ans = {'index':photo.params['edited'],'pixbuf':pixbuf,'photo_name':photo_name,'photo':photo}				
	print('dai',pixbuf)
	return pixbuf, ans
	
def upload_an_image(picasa, reduce_size, size, colors, album_id, filename, title, comment):
	uploaded = False
	while not uploaded:
		try:
			photo = picasa.add_image(album_id,filename,title,comment,reduce_size,size,colors)
			uploaded = True
		except Exception as e:
			logging.info(e)
			wait(await)
			await += .1
	if photo is not None:
		photo_name=photo.params['title']
		mdir = os.path.join(comun.IMAGES_DIR,'album_'+album_id)
		if not os.path.exists(mdir):
			os.makedirs(mdir)
		mfile = os.path.join(mdir,'photo_'+photo.params['id']+'.png')
		if os.path.exists(mfile):
			os.remove(mfile)
		create_icon(mfile,photo.params['thumbnail2'],photo.params['access'])
		if os.path.exists(mfile):
			pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
		else:
			pixbuf = PIXBUF_DEFAULT_PHOTO
		ans = {'index':photo.params['edited'],'pixbuf':pixbuf,'photo_name':photo_name,'photo':photo}				
		return ans
	return None

class MinimalButton(Gtk.Button):
	def __init__(self, file_image_active, file_image_inactive):
		Gtk.Button.__init__(self)
		self.set_name('minimal_button')
		self.image_active = Gtk.Image.new_from_file(os.path.join(comun.IMGDIR,file_image_active+'.svg'))
		self.image_inactive = Gtk.Image.new_from_file(os.path.join(comun.IMGDIR,file_image_inactive+'.svg'))
		self.set_sensitive(True)

	def set_sensitive(self,sensitive):
		Gtk.Button.set_sensitive(self,sensitive)
		if sensitive:
			self.set_image(self.image_active)
		else:
			self.set_image(self.image_inactive)
			
		

class Picapy(Gtk.Window):
	
	def __init__(self):
		Gtk.Window.__init__(self)
		self.set_name('MyWindow')
		#self.set_property("type",Gtk.WindowType.POPUP)
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_title(comun.APP)
		self.set_default_size(900, 600)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.close_application)
		#
		self.image_dir = os.getenv('HOME')
		self.picasa = Picasa(token_file = comun.TOKEN_FILE)
		error = True
		while(error):
			if self.picasa.do_refresh_authorization() is None:
				authorize_url = self.picasa.get_authorize_url()
				ld = LoginDialog(authorize_url)
				ld.run()
				self.picasa.get_authorization(ld.code)
				ld.destroy()				
				if self.picasa.do_refresh_authorization() is None:
					md = Gtk.MessageDialog(	parent = self,
											flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
											type = Gtk.MessageType.ERROR,
											buttons = Gtk.ButtonsType.OK_CANCEL,
											message_format = _('You have to authorize Picapy to use it, do you want to authorize?'))
					if md.run() == Gtk.ResponseType.CANCEL:
						exit(3)				
				else:
					self.picasa = Picasa(token_file = comun.TOKEN_FILE)
					if self.picasa.do_refresh_authorization() is None:
						error = False
					self.load_preferences()
			else:
				self.load_preferences()
				error = False
		#
		vbox = Gtk.VBox()
		self.add(vbox)
		#
		self.menubar = Gtk.MenuBar.new()
		vbox.pack_start(self.menubar,False,False,0)	
		################################################################
		self.filemenu = Gtk.Menu.new()
		self.filem = Gtk.MenuItem.new_with_label(_('File'))
		self.filem.set_submenu(self.filemenu)
		#
		self.sal = Gtk.ImageMenuItem.new_with_label(_('Exit'))
		self.sal.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_QUIT, Gtk.IconSize.MENU))		
		self.sal.set_always_show_image(True)
		self.sal.connect('activate',self.close_application)
		self.filemenu.append(self.sal)
		#
		self.menubar.append(self.filem)
		################################################################
		self.fileedit = Gtk.Menu.new()
		self.filee = Gtk.MenuItem.new_with_label(_('Edit'))
		self.filee.set_submenu(self.fileedit)
		#
		self.pref = Gtk.ImageMenuItem.new_with_label(_('Preferences'))
		self.pref.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_PREFERENCES, Gtk.IconSize.MENU))		
		self.pref.connect('activate',self.on_preferences_activate)
		self.pref.set_always_show_image(True)
		self.fileedit.append(self.pref)
		#
		self.download_all = Gtk.MenuItem.new_with_label(_('Download all albums'))
		self.download_all.connect('activate',self.on_download_all_activate)
		self.fileedit.append(self.download_all)
		#
		self.menubar.append(self.filee)
		################################################################
		self.filehelp = Gtk.Menu.new()
		self.fileh = Gtk.MenuItem.new_with_label(_('Help'))
		self.fileh.set_submenu(self.get_help_menu())
		#
		self.menubar.append(self.fileh)
		################################################################
		#
		vbox1 = Gtk.VBox(spacing = 0)
		vbox1.set_border_width(0)
		vbox.add(vbox1)
		#
		hbox = Gtk.HBox()
		vbox1.pack_start(hbox,True,True,0)
		#
		vbox3 = Gtk.VBox()
		hbox.pack_start(vbox3,True,True,0)
		#
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)		
		vbox3.pack_start(scrolledwindow,True,True,0)
		self.iconview1 = Gtk.IconView()
		self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
		scrolledwindow.add(self.iconview1)
		#
		'''
		self.progressbar = Gtk.ProgressBar()
		vbox3.pack_start(self.progressbar,False,False,0)
		self.progressbar.hide()
		'''
		backgroundVBox2 = Gtk.EventBox()		
		hbox.pack_start(backgroundVBox2,False,False,0)
		#
		vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=0)
		vbox2.set_border_width(5)
		backgroundVBox2.add(vbox2)
		#
		self.button1 = MinimalButton('up_active','up_inactive')
		self.button1.set_size_request(40,40)
		self.button1.set_tooltip_text(_('Up'))	
		self.button1.connect('clicked',self.on_button1_clicked)
		self.button1.set_sensitive(False)
		vbox2.pack_start(self.button1,False,False,0)
		#
		self.button2 = MinimalButton('add_active','add_inactive')
		self.button2.set_size_request(40,40)
		self.button2.set_tooltip_text(_('Add'))	
		self.button2.connect('clicked',self.on_button2_clicked)
		vbox2.pack_start(self.button2,False,False,0)
		#
		self.button3 = MinimalButton('remove_active','remove_inactive')
		self.button3.set_size_request(40,40)
		self.button3.set_tooltip_text(_('Remove'))		
		self.button3.connect('clicked',self.on_remove_button_clicked)
		vbox2.pack_start(self.button3,False,False,0)
		#
		self.button_download = MinimalButton('download_active','download_inactive')
		self.button_download.set_size_request(40,40)
		self.button_download.set_tooltip_text(_('Download'))	
		self.button_download.connect('clicked',self.on_descargar_activated)		
		vbox2.pack_start(self.button_download,False,False,0)
		#
		self.button_preview = MinimalButton('slideshow_active','slideshow_inactive')
		self.button_preview.set_size_request(40,40)
		self.button_preview.set_tooltip_text(_('Slideshow'))	
		self.button_preview.connect('clicked',self.on_preview_activated)
		self.button_preview.set_sensitive(False)		
		vbox2.pack_start(self.button_preview,False,False,0)
		#
		self.button4 = MinimalButton('exit_active','exit_inactive')
		self.button4.set_size_request(40,40)
		self.button4.set_tooltip_text(_('Exit from Picapy'))		
		self.button4.connect('clicked',self.close_application)
		vbox2.pack_end(self.button4,False,False,0)
		#
		self.menu_emergente=Gtk.Menu()
		self.menuitem3 = Gtk.MenuItem.new_with_label(_('Information'))
		self.menuitem3.connect('activate',self.on_informacion_activated)
		self.menu_emergente.append(self.menuitem3)
		self.menuitem4 = Gtk.MenuItem.new_with_label(_('Edit'))
		self.menuitem4.connect('activate',self.on_edit_activated)
		self.menu_emergente.append(self.menuitem4)
		self.menuitem5 = Gtk.MenuItem.new_with_label(_('Download'))
		self.menuitem5.connect('activate',self.on_descargar_activated)
		self.menu_emergente.append(self.menuitem5)
		self.menuitem6 = Gtk.MenuItem.new_with_label(_('Copy link to clipboard'))
		self.menuitem6.connect('activate',self.on_menuitem6_activated)
		self.menu_emergente.append(self.menuitem6)
		self.menuitem7 = Gtk.MenuItem.new_with_label(_('Copy thumbnail 72x72 link to clipboard'))
		self.menuitem7.connect('activate',self.on_menuitem7_activated)
		self.menu_emergente.append(self.menuitem7)
		self.menuitem8 = Gtk.MenuItem.new_with_label(_('Copy thumbnail 144x144 link to clipboard'))
		self.menuitem8.connect('activate',self.on_menuitem8_activated)
		self.menu_emergente.append(self.menuitem8)
		self.menuitem9 = Gtk.MenuItem.new_with_label(_('Copy thumbnail 288x288 link to clipboard'))
		self.menuitem9.connect('activate',self.on_menuitem9_activated)
		self.menu_emergente.append(self.menuitem9)
		self.menuitem10 = Gtk.MenuItem.new_with_label(_('Copy link for web'))
		self.menuitem10.connect('activate',self.on_menuitem10_activated)
		self.menu_emergente.append(self.menuitem10)
		self.menuitem11 = Gtk.MenuItem.new_with_label(_('Copy image'))
		self.menuitem11.connect('activate',self.on_menuitem11_activated)
		self.menu_emergente.append(self.menuitem11)
		self.menuitem12 = Gtk.MenuItem.new_with_label(_('Paste image'))
		self.menuitem12.connect('activate',self.on_menuitem12_activated)
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
		self.store = Gtk.ListStore(GdkPixbuf.Pixbuf,str,GObject.TYPE_PYOBJECT)
		self.storeimages = Gtk.ListStore(GdkPixbuf.Pixbuf,str,GObject.TYPE_PYOBJECT)
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
		self.iconview1.connect('button-press-event',self.on_iconview1_button_press_event)
		self.iconview1.connect('button-release-event',self.on_iconview1_button_release_event)

		self.iconview1.connect('key-release-event',self.on_iconview1_key_release_event)
		# set icon for drag operation
		self.iconview1.connect('drag-begin', self.drag_begin)
		self.iconview1.connect('drag-data-get', self.drag_data_get_data)
		self.iconview1.connect('drag-data-received',self.drag_data_received)
		#
		dnd_list = [Gtk.TargetEntry.new('text/uri-list', 0, 100),Gtk.TargetEntry.new('text/plain', 0, 80)]
		self.iconview1.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, dnd_list, Gdk.DragAction.COPY)
		self.iconview1.drag_source_add_uri_targets()
		dnd_list = Gtk.TargetEntry.new("text/uri-list", 0, 0)
		self.iconview1.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.HIGHLIGHT | Gtk.DestDefaults.DROP,[dnd_list],Gdk.DragAction.MOVE )
		self.iconview1.drag_dest_add_uri_targets()
		#
		self.album = None
		#
		style_provider = Gtk.CssProvider()
		css = """
			GtkEventBox{
				background-color: rgba(60, 60, 60, 255);
			}
			#minimal_button {
				border-image: none;
				background-image: none;
				background-color: rgba(60, 60, 60, 255);				
				border-radius: 0px;
			}
			#minimal_button:hover {
				transition: 1000ms linear;
				background-image: none;
				border-image: none;
				background-color: rgba(150, 150, 150, 255);
			}
			#navigator_button {
				border-image: none;
				background-image: none;
				background-color: rgba(0, 0, 0, 0);
				border-radius: 0px;
			}
			#navigator_button:hover {
				transition: 1000ms linear;
				background-image: none;
				border-image: none;
				background-color: rgba(150, 150, 150, 255);
			}
		"""
		style_provider.load_from_data(css.encode('UTF-8'))
		Gtk.StyleContext.add_provider_for_screen(
			Gdk.Screen.get_default(), 
			style_provider,     
			Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
		)
		#
		self.show_all()
		#
		self.set_wait_cursor()
		self.inicia_albums()
		self.set_normal_cursor()
	
		
	def increase(self):
		self.progress_bar_value+=1.0
		fraction=self.progress_bar_value/self.progress_bar_max_value
		self.progressbar.set_fraction(fraction)
		while Gtk.events_pending():
			Gtk.main_iteration()
		if self.progress_bar_value==self.progress_bar_max_value:
			self.progressbar.hide()
			
	def drag_begin(self, widget, context):
		if self.album != None:			
			items = self.iconview1.get_selected_items()
			if len(items)>0:
				selected=self.storeimages.get_iter_from_string(str(items[0]))
				pixbuf = self.storeimages.get_value(selected,0)
				Gtk.drag_set_icon_pixbuf(context, pixbuf, -2, -2)						

	def drag_data_get_data(self, treeview, context, selection, target_id, etime):
		if target_id == 0:
			if self.album != None:
				items = self.iconview1.get_selected_items()
				files = []
				if len(items)>0:
					selected=self.storeimages.get_iter_from_string(str(items[0]))
					imagen=self.storeimages.get_value(selected,2)
					if imagen.params['url'].rfind('/')>-1:
						ext = imagen.params['url'][-4:]
						name = self.storeimages.get_value(selected,1)
						if name[-4:] != ext:
							name =name+ext
						filename = tempfile.mkstemp(suffix = '',prefix='picapy_tmp', dir='/tmp')[1]
						download_image(imagen.params['url'],filename)
						#
						if os.path.exists(filename):
							newname = os.path.join('/tmp',name)
							os.rename(filename,newname)
							if os.path.exists(filename):
								os.remove(filename)
						location = "file://" + newname
						files.append(location)	   
						selection.set_uris(files)						

	def drag_data_received(self,widget, drag_context, x, y, selection_data, info, timestamp):
		if self.album!=None:
			filenames = selection_data.get_uris()
			logging.info(filenames)
			for_upload = []
			for filename in filenames:
				if len(filename)>8:
					filename = urllib.request.url2pathname(filename)
					filename = filename[7:]
					mime = mimetypes.guess_type(filename)
					if os.path.exists(filename):
						mime = mimetypes.guess_type(filename)[0]
						logging.info(mime)
						if mime in googlepicasaapi.SUPPORTED_MIMES or mime in googlepicasaapi.CONVERTED_MIMES:
							logging.info(filename)
							for_upload.append(filename)
			if len(for_upload)>0:
				self.set_wait_cursor()					
				jobs = []
				with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
					for filename in for_upload:
						job = executor.submit(upload_an_image, self.picasa, self.reduce_size, self.max_size, self.reduce_colors, self.album.params['id'], filename, os.path.basename(filename), None)
						jobs.append(job)
				results = []
				for job in concurrent.futures.as_completed(jobs):
					results.append(job.result())
				sorted(results, key=lambda element: element['index'])
				for element in results:
					self.storeimages.prepend([element['pixbuf'],element['photo_name'],element['photo']])
				self.set_normal_cursor()
				while Gtk.events_pending():
					Gtk.main_iteration()		
		return True
		
	def load_preferences(self):
		configuration = Configuration()
		self.image_link = configuration.get('image_link')
		self.max_size = configuration.get('max_size')
		self.reduce_size = configuration.get('reduce_size')
		self.reduce_colors = configuration.get('reduce_colors')
		self.image_dir = configuration.get('image_dir')
		self.time_between_images = configuration.get('time_between_images')
		if self.image_dir is None or len(self.image_dir)<=0 or os.path.exists(self.image_dir)==False:
			self.image_dir = os.getenv('HOME')
		self.first_time = configuration.get('first_time')

	def get_help_menu(self):
		help_menu =Gtk.Menu()
		#		
		add2menu(help_menu,text = _('Web...'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://launchpad.net/picapy'))
		add2menu(help_menu,text = _('Get help online...'),conector_event = 'activate',conector_action = lambda x:webbrowser.open('https://answers.launchpad.net/picapy'))
		add2menu(help_menu,text = _('Translate this application...'),conector_event = 'activate',conector_action =lambda x:webbrowser.open('https://translations.launchpad.net/picapy'))
		add2menu(help_menu,text = _('Report a bug...'),conector_event = 'activate',conector_action = lambda x:webbrowser.open('https://bugs.launchpad.net/picapy'))
		add2menu(help_menu)
		web = add2menu(help_menu,text = _('Homepage'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('http://www.atareao.es/tag/picapy'))
		twitter = add2menu(help_menu,text = _('Follow us in Twitter'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://twitter.com/atareao'))
		googleplus = add2menu(help_menu,text = _('Follow us in Google+'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('https://plus.google.com/118214486317320563625/posts'))
		facebook = add2menu(help_menu,text = _('Follow us in Facebook'),conector_event = 'activate',conector_action = lambda x: webbrowser.open('http://www.facebook.com/elatareao'))
		add2menu(help_menu)
		add2menu(help_menu,text = _('About'),conector_event = 'activate',conector_action = self.on_about_activate)
		#		
		web.set_image(Gtk.Image.new_from_file(os.path.join(comun.IMGDIR,'web.svg')))
		web.set_always_show_image(True)
		twitter.set_image(Gtk.Image.new_from_file(os.path.join(comun.IMGDIR,'twitter.svg')))
		twitter.set_always_show_image(True)
		googleplus.set_image(Gtk.Image.new_from_file(os.path.join(comun.IMGDIR,'googleplus.svg')))
		googleplus.set_always_show_image(True)
		facebook.set_image(Gtk.Image.new_from_file(os.path.join(comun.IMGDIR,'facebook.svg')))
		facebook.set_always_show_image(True)
		#
		help_menu.show()
		return help_menu				
	def inicia_images(self):
		modelo = Gtk.ListStore(str)
		self.treeview2.set_model(modelo)
		render=Gtk.CellRendererText()
		columna=Gtk.TreeViewColumn("Imagen",render,text=0)
		self.treeview2.append_column(columna)
		#
	def close_application(self,widget):
		configuration = Configuration()
		configuration.set('image_dir',self.image_dir)
		configuration.save()
		main_thread = threading.currentThread()
		for t in threading.enumerate():
			logging.info(t)
			if t is main_thread:
				continue
			t.join()		
		exit(0)
		
	def prepend_album(self,album):
		album_name=album.params['title']
		mfile = os.path.join(comun.IMAGES_DIR,'album_'+album.params['id']+'.png')
		if os.path.exists(mfile):
			os.remove(mfile)
		create_icon(mfile,album.params['thumbnail2'],album.params['access'])
		if os.path.exists(mfile):
			pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
		else:
			pixbuf = PIXBUF_DEFAULT_ALBUM
		self.store.prepend()		
		iter = self.store.get_iter_first()
		self.store.set_value(iter,0,pixbuf)
		self.store.set_value(iter,1,album_name)
		self.store.set_value(iter,2,album)
	
	def inicia_albums(self):
		data_file = os.path.join(comun.IMAGES_DIR,'album.data')
		data = None
		if os.path.exists(data_file):
			f=codecs.open(data_file,'r','utf-8')
			data = json.loads(f.read())
			f.close()
		self.store.clear()
		self.albums=self.picasa.get_albums()		
		if len(self.albums)>0:
			to_json = {}
			with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_THREADS) as executor:
				for album in self.albums:
					to_json[album.params['id']]=album.params
					if data is None or album.params['id'] not in data.keys() or (data[album.params['id']]['etag'] != album.params['etag']):						
						executor.submit(create_icon_for_album,album)
			for album in self.albums:
				mfile = os.path.join(comun.IMAGES_DIR,'album_'+album.params['id']+'.png')
				if os.path.exists(mfile):
					pixbuf = get_pixbuf_from_url('file://'+mfile)
				else:
					pixbuf = PIXBUF_DEFAULT_ALBUM				
				self.store.append([pixbuf,album.params['title'],album])
			while Gtk.events_pending():
				Gtk.main_iteration()
			f=open(data_file,'w')
			f.write(json.dumps(to_json))
			f.close()

	def on_edit_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			if self.album==None:
				selected=self.store.get_iter_from_string(str(items[0]))
				album = self.store.get_value(selected,2)
				i=EditAlbum(self,album)				
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
						album_name=album.params['title']					
						mfile = os.path.join(comun.IMAGES_DIR,'album_'+album.params['id']+'.png')
						os.remove(mfile)
						create_icon(mfile,updated_album.params['thumbnail2'],updated_album.params['access'])
						if os.path.exists(mfile):
							pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
						else:
							pixbuf = PIXBUF_DEFAULT_ALBUM					
						self.store.set_value(selected,0,pixbuf)
						self.store.set_value(selected,1,updated_album.params['title'])
						self.store.set_value(selected,2,updated_album)
					'''
					self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))					
					self.inicia_albums()
					self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))			
					'''
				i.destroy()
			else:
				selected=self.storeimages.get_iter_from_string(str(items[0]))
				image = self.storeimages.get_value(selected,2)
				i=EditImage(self,image)				
				if i.run() == Gtk.ResponseType.ACCEPT:
					logging.info('*******************************************')
					logging.info(i.filename)
					logging.info('*******************************************')
					updated_image = self.picasa.edit_photo(self.album.params['id'],image,i.filename,caption=i.entry2.get_text())
					logging.info(updated_image)
					if updated_image is not None:
						mdir = os.path.join(comun.IMAGES_DIR,'album_'+self.album.params['id'])
						if not os.path.exists(mdir):
							os.makedirs(mdir)
						mfile = os.path.join(mdir,'photo_'+updated_image.params['id']+'.png')
						if os.path.exists(mfile):
							os.remove(mfile)
						create_icon(mfile,updated_image.params['thumbnail2'],updated_image.params['access'])
						if os.path.exists(mfile):
							pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
						else:
							pixbuf = PIXBUF_DEFAULT_PHOTO
						self.storeimages.set_value(selected,0,pixbuf)
						self.storeimages.set_value(selected,1,updated_image.params['title'])
						self.storeimages.set_value(selected,2,updated_image)
				i.destroy()

	def on_informacion_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			if self.album==None:
				selected=self.store.get_iter_from_string(str(items[0]))
				i=InformacionAlbum(self,self.store.get_value(selected,2))
				i.run()
				i.destroy()
			else:
				selected=self.storeimages.get_iter_from_string(str(items[0]))
				i=InformacionImagen(self,self.storeimages.get_value(selected,2))
				i.run()
				i.destroy()

	def on_preferences_activate(self,widget):
		p = Preferences(self)
		if p.run() == Gtk.ResponseType.ACCEPT:
			p.save_preferences()
		p.destroy()						
		self.load_preferences()
		self.picasa = Picasa(token_file = comun.TOKEN_FILE)
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
					md = Gtk.MessageDialog(	parent = self,
											flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
											type = Gtk.MessageType.ERROR,
											buttons = Gtk.ButtonsType.OK_CANCEL,
											message_format = _('You have to authorize Picapy to use it, do you want to authorize?'))
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
		self.button1.set_sensitive(False)
		self.button_preview.set_sensitive(False)
		self.album=None
		self.set_title('Picapy')
	def on_preview_activated(self,widget):
		if self.album is not None:
			images = []
			items = self.iconview1.get_selected_items()
			if len(items)>0:				
				for item in items:
					selected=self.storeimages.get_iter_from_string(str(item))
					image=self.storeimages.get_value(selected,2)
					images.append(image)
			else:
				itera = self.storeimages.get_iter_first()
				while(itera):
					image=self.storeimages.get_value(itera,2)
					images.append(image)
					itera = self.storeimages.iter_next(itera)			
			sw = SliderWindow(images,self.time_between_images)
						
	def on_download_all_activate(self,widget):
		chooser = Gtk.FileChooserDialog(title=_('Select where to download all albums'),parent=self,action=Gtk.FileChooserAction.SELECT_FOLDER,buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		chooser.set_current_folder(self.image_dir)
		if chooser.run() == Gtk.ResponseType.OK:
			filename=chooser.get_filename()
			self.image_dir = os.path.dirname(filename)
			if self.image_dir is None or len(self.image_dir)<=0 or os.path.exists(self.image_dir)==False:
				self.image_dir = os.getenv('HOME')
			chooser.destroy()
			albums = self.picasa.get_albums()				
			if len(albums)>0:
				progreso=Progreso(_('Downloading all albums...'),self,len(albums))
				self.set_wait_cursor()
				allphotos = []
				for album in albums:
					folder = os.path.join(filename,album.params['id'])
					if not os.path.exists(folder):
						os.mkdir(folder)
					photos=self.picasa.get_photos(album.params['id'])
					with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_THREADS) as executor:
						for index,photo in enumerate(photos):
							executor.submit(download_all_images,folder,photo)
					progreso.increase()
					while Gtk.events_pending():
						Gtk.main_iteration()
			self.set_normal_cursor()
		chooser.destroy()
			
	def on_about_activate(self,widget):
		ad=Gtk.AboutDialog()
		ad.set_name(comun.APPNAME)
		ad.set_version(comun.VERSION)
		ad.set_copyright('Copyrignt (c) 2010-2014\nLorenzo Carbonell')
		ad.set_comments(_('An application to manage your images in\nPicasa Web'))
		ad.set_license(''+
		'This program is free software: you can redistribute it and/or modify it\n'+
		'under the terms of the GNU General Public License as published by the\n'+
		'Free Software Foundation, either version 3 of the License, or (at your option)\n'+
		'any later version.\n\n'+
		'This program is distributed in the hope that it will be useful, but\n'+
		'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n'+
		'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n'+
		'more details.\n\n'+
		'You should have received a copy of the GNU General Public License along with\n'+
		'this program.  If not, see <http://www.gnu.org/licenses/>.')
		ad.set_website('http://www.atareao.es')
		ad.set_website_label('http://www.atareao.es')
		ad.set_authors(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_documenters(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_translator_credits(''+
		'Dario Villar Veres <dario.villar.v@gmail.com>\n'+
		'Bernardo Miguel	Savone <bmsavone@gmail.com>\n'+
		'Enbata <peionz@euskalnet.net>\n'+
		'Mario Blättermann <mariobl@gnome.org>\n'+
		'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>\n'+
		'zeugma <https://launchpad.net/~sunder67>\n'+
		'Alin Andrei <https://launchpad.net/~nilarimogard>\n'+
		'Fitoschido <fitoschido@gmail.com>\n'+
		'Daniele Lucarelli <https://launchpad.net/~ldanivvero>\n'+
		'Alejandro Martín Covarrubias <alex.covarrubias@gmail.com>\n'+
		'Rustam Vafin\n'+
		'elmodos\n'+
		'extraymond@gmail.com <extraymond@gmail.com>\n'+
		'fgp <https://launchpad.net/~komakino>\n')
		ad.set_program_name('Picapy')
		ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
		ad.run()
		ad.destroy()

	def set_wait_cursor(self):
		self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))					
		while Gtk.events_pending():
			Gtk.main_iteration()		
	def set_normal_cursor(self):
		self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))			
		while Gtk.events_pending():
			Gtk.main_iteration()		

	def on_descargar_activated(self,widget):		
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			if self.album==None:
				chooser = Gtk.FileChooserDialog(title=_('Select where to download the album'),parent=self,action=Gtk.FileChooserAction.SELECT_FOLDER,buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
				chooser.set_current_folder(self.image_dir)
				if chooser.run() == Gtk.ResponseType.OK:
					filename=chooser.get_filename()
					self.image_dir = os.path.dirname(filename)
					if self.image_dir is None or len(self.image_dir)<=0 or not os.path.exists(self.image_dir):
						self.image_dir = os.getenv('HOME')									
					chooser.destroy()
					if len(items)>0:
						self.set_wait_cursor()
						daemons = []
						global cuain
						cuain = queue.Queue()
						for item in items:
							itera = self.store.get_iter_from_string(str(item))
							album=self.store.get_value(itera,2)
							folder = os.path.join(filename,album.params['id'])
							if not os.path.exists(folder):
								os.mkdir(folder)
							photos=self.picasa.get_photos(album.params['id'])
							#		
							with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_THREADS) as executor:
								for photo in photos:
									executor.submit(download_all_images,folder,photo)

						self.set_normal_cursor()					
				chooser.destroy()
			else:
				chooser = Gtk.FileChooserDialog(title=_('Select where download images'),parent=self,action=Gtk.FileChooserAction.SELECT_FOLDER,buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
				if chooser.run() == Gtk.ResponseType.OK:
					dirname=chooser.get_filename()
					chooser.destroy()
					self.set_wait_cursor()
					for item in items:
						selected=self.storeimages.get_iter_from_string(str(item))
						imagen=self.storeimages.get_value(selected,2)
						filename = imagen.params['url'].split('/')[-1]
						filename = os.path.join(dirname,filename)
						logging.info(filename)
						download_image(imagen.params['url'],filename)
					self.set_normal_cursor()
			
	def on_menuitem6_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			selected=self.storeimages.get_iter_from_string(str(items[0]))
			imagen=self.storeimages.get_value(selected,2)
			text = imagen.params['url']
			atom = Gdk.atom_intern('CLIPBOARD', True)
			clipboard = self.iconview1.get_clipboard(atom)
			clipboard.set_text(text, -1)

	def on_menuitem7_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			selected=self.storeimages.get_iter_from_string(str(items[0]))
			imagen=self.storeimages.get_value(selected,2)
			text = imagen.thumbnails[0]['url']
			atom = Gdk.atom_intern('CLIPBOARD', True)
			clipboard = self.iconview1.get_clipboard(atom)
			clipboard.set_text(text, -1)

	def on_menuitem8_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			selected=self.storeimages.get_iter_from_string(str(items[0]))
			imagen=self.storeimages.get_value(selected,2)
			text = imagen.thumbnails[1]['url']
			atom = Gdk.atom_intern('CLIPBOARD', True)
			clipboard = self.iconview1.get_clipboard(atom)
			clipboard.set_text(text, -1)

	def on_menuitem9_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			selected=self.storeimages.get_iter_from_string(str(items[0]))
			imagen=self.storeimages.get_value(selected,2)
			text = imagen.thumbnails[2]['url']
			atom = Gdk.atom_intern('CLIPBOARD', True)
			clipboard = self.iconview1.get_clipboard(atom)
			clipboard.set_image(text, -1)


	def on_menuitem10_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			selected=self.storeimages.get_iter_from_string(str(items[0]))
			imagen=self.storeimages.get_value(selected,2)
			#text = '<a class="highslide" title="%TITLE%" onclick="return hs.expand(this)" href="%URL%"> <img class="aligncenter" title="%TITLE%" src="%URL288%" alt="%TITLE%"/></a>'
			text = self.image_link
			text = text.replace('%TITLE%',imagen.params['title'])
			text = text.replace('%URL%',imagen.params['url'])
			text = text.replace('%URL72%',imagen.thumbnails[0]['url'])
			text = text.replace('%URL144%',imagen.thumbnails[1]['url'])
			text = text.replace('%URL288%',imagen.thumbnails[2]['url'])			
			atom = Gdk.atom_intern('CLIPBOARD', True)
			clipboard = self.iconview1.get_clipboard(atom)
			clipboard.set_text(text, -1)
	
	def on_menuitem11_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			selected=self.storeimages.get_iter_from_string(str(items[0]))
			imagen = self.storeimages.get_value(selected,2)		
			pixbuf = get_pixbuf_from_url(imagen.params['url'])
			atom = Gdk.atom_intern('CLIPBOARD', True)
			clipboard = self.iconview1.get_clipboard(atom)
			clipboard.set_image(pixbuf)
			clipboard.store()
			
	def on_menuitem12_activated(self,widget):
		if self.album != None:
			atom = Gdk.atom_intern('CLIPBOARD', True)
			clipboard = Gtk.Clipboard.get(atom)
			pixbuf = clipboard.wait_for_image() 
			logging.info(self.album.params['id'])
			if pixbuf != None:
				ia = PasteImage(self,None)
				if ia.run() == Gtk.ResponseType.ACCEPT:
					titulo = ia.entry1.get_text()
					sumario = ia.entry2.get_text()
					ia.destroy()
					if titulo!=None and len(titulo)>0:
						photo = self.picasa.add_image_from_pixbuf(self.album.params['id'],pixbuf,titulo,sumario,self.reduce_size,self.max_size,self.reduce_colors)
						mdir = os.path.join(comun.IMAGES_DIR,'album_'+self.album.params['id'])
						if not os.path.exists(mdir):
							os.makedirs(mdir)
						mfile = os.path.join(mdir,'photo_'+photo.params['id']+'.png')						
						create_icon(mfile,photo.params['thumbnail2'],photo.params['access'])
						if os.path.exists(mfile):
							pixbuf = GdkPixbuf.Pixbuf.new_from_file(mfile)
						else:
							pixbuf = PIXBUF_DEFAULT_PHOTO
						self.storeimages.prepend([pixbuf,titulo,photo])
				ia.destroy()

	def on_iconview1_button_press_event(self,widget,event):
		#
		# if event.button==1 and event.type==Gdk.BUTTON_PRESS:
		#
		# Gdk.EventType.2BUTTON_PRESS is not working in python because
		# it starts with number so use Gdk.EventType(value = 5) to construct
		# 2BUTTON_PRESS event type
		if event.button == 1 and event.type == Gdk.EventType(value=5):		
			if self.album==None:
				items = self.iconview1.get_selected_items()
				if len(items)>0:
					selected=self.store.get_iter_from_string(str(items[0]))
					self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
					while Gtk.events_pending():
						Gtk.main_iteration()								
					self.load_images_from_picasa_album(self.store.get_value(selected,2))
					self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))	
			else:
				items = self.iconview1.get_selected_items()
				if len(items)>0:
					selected=self.storeimages.get_iter_from_string(str(items[0]))
					image=self.storeimages.get_value(selected,2)
					v = VerImagen(self,image)
					v.run()
					v.destroy()

	def on_iconview1_button_release_event(self,widget,event):
		if event.button == 3:
			items = self.iconview1.get_selected_items()
			if len(items)>0:
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
					#self.menuitem13.set_sensitive(False)
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
					#self.menuitem13.set_sensitive(True)
				self.menu_emergente.popup( None, None, None, None, 0, 0)
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
				#self.menuitem13.set_sensitive(False)
				self.menu_emergente.popup( None, None, None, None, 0, 0)
	def on_iconview1_key_release_event(self,widget,event):
		values = []
		values.append(Gdk.keyval_from_name('Return'))
		values.append(Gdk.keyval_from_name('KP_Enter'))
		values.append(Gdk.keyval_from_name('space'))
		if event.keyval in values:
			if self.album==None:
				items = self.iconview1.get_selected_items()
				if len(items)>0:
					selected=self.store.get_iter_from_string(str(items[0]))
					self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
					while Gtk.events_pending():
						Gtk.main_iteration()								
					self.load_images_from_picasa_album(self.store.get_value(selected,2))
					self.get_root_window().set_cursor(Gdk.Cursor(Gdk.CursorType.ARROW))	
			else:
				items = self.iconview1.get_selected_items()
				if len(items)>0:
					selected=self.storeimages.get_iter_from_string(str(items[0]))
					image=self.storeimages.get_value(selected,2)
					v = VerImagen(self,image)
					v.run()
					v.destroy()	
		elif event.keyval == Gdk.keyval_from_name('BackSpace'):
			if self.album != None:
				self.iconview1.set_model(self.store)
				self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
				self.button1.set_sensitive(False)
				self.button_preview.set_sensitive(False)
				self.album=None
				self.set_title('Picapy')		
		
	def load_images_from_picasa_album(self,album):
		self.set_title('Picapy | ' + album.params['title'])
		mdir = os.path.join(comun.IMAGES_DIR,'album_'+album.params['id'])
		if not os.path.exists(mdir):
			os.makedirs(mdir)
		data_file = os.path.join(mdir,'photo.data')		
		data = None
		if os.path.exists(data_file):
			f=codecs.open(data_file,'r','utf-8')
			data = json.loads(f.read())
			f.close()		
		photos=self.picasa.get_photos(album.params['id'])
		self.storeimages.clear()		
		self.iconview1.set_model(self.storeimages)
		self.iconview1.show()
		while Gtk.events_pending():
			Gtk.main_iteration()		
		self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
		if len(photos)>0:			
			results = []
			to_json = {}
			photos.sort()
			with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_THREADS) as executor:
				for photo in photos:
					to_json[photo.params['id']]=photo.params
					if data is None or (photo.params['id'] not in data.keys()) or (data[photo.params['id']]['etag'] != photo.params['etag']):
						executor.submit(create_icon_for_photo,album.params['id'],photo)
			mdir = os.path.join(comun.IMAGES_DIR,'album_'+album.params['id'])
			if not os.path.exists(mdir):
				os.makedirs(mdir)
			for photo in photos:
				photo_name=photo.params['title']
				mfile = os.path.join(mdir,'photo_'+photo.params['id']+'.png')
				if os.path.exists(mfile):
					pixbuf = get_pixbuf_from_url('file://'+mfile)
				else:
					pixbuf = PIXBUF_DEFAULT_PHOTO
				self.storeimages.append([pixbuf,photo.params['title'],photo])
			f=open(data_file,'w')
			f.write(json.dumps(to_json))
			f.close()

		self.album=album
		self.button1.set_sensitive(True)
		self.button_preview.set_sensitive(True)
		self.button_download.set_sensitive(True)
			
	def on_button1_clicked(self,widget):
		self.iconview1.set_model(self.store)
		self.iconview1.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
		self.button1.set_sensitive(False)
		self.button_preview.set_sensitive(False)
		self.album=None
		self.set_title('Picapy')
			
	def on_remove_button_clicked(self,widget):
		if self.album==None:
			items = self.iconview1.get_selected_items()
			if len(items)>0:
				if len(items)>1:
					msg = _('Do you want to delete %s folders?') % str(len(items))
					msg2 = _('Deleting folders...')
				else:
					msg = _('Do you want to delete this folder?')
					msg2 = _('Deleting folder...')
				md = Gtk.MessageDialog(self, 
				Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, 
				Gtk.ButtonsType.OK_CANCEL, msg)
				respuesta=md.run()
				if respuesta == Gtk.ResponseType.OK:
					md.destroy()
					p=Progreso(msg2,self,len(items))
					for item in items:
						itera = self.store.get_iter_from_string(str(item))
						selected=self.store.get_value(itera,2)
						if self.picasa.delete_album(selected):
							self.store.remove(itera)
						p.increase()
					p.destroy()
				else:
					md.destroy()
		else:
			items = self.iconview1.get_selected_items()
			if len(items)>0:
				if len(items)>1:
					msg = _('Do you want to delete %s images?') % str(len(items))
					msg2 = _('Deleting images...')
				else:
					msg = _('Do you want to delete this image?')
					msg2 = _('Deleting image...')
				md = Gtk.MessageDialog(self, 
				Gtk.DialogFlags.DESTROY_WITH_PARENT, Gtk.MessageType.QUESTION, 
				Gtk.ButtonsType.OK_CANCEL, msg)
				respuesta=md.run()
				if respuesta == Gtk.ResponseType.OK:			
					md.destroy()
					p=Progreso(msg2,self,len(items))
					for item in items:
						itera = self.storeimages.get_iter_from_string(str(item))
						selected=self.storeimages.get_value(itera,2)
						if self.picasa.delete_photo(self.album,selected):
							self.storeimages.remove(itera)
						p.increase()
					p.destroy()
				else:
					md.destroy()
			
	def update_preview_cb(self,file_chooser, preview):
		filename = file_chooser.get_preview_filename()
		try:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 128, 128)
			preview.set_from_pixbuf(pixbuf)
			have_preview = True
		except:
			have_preview = False
		file_chooser.set_preview_widget_active(have_preview)
		return

	def on_button2_clicked(self,widget):
		if self.album==None:
			n=NuevoAlbum(self)
			if n.run() == Gtk.ResponseType.ACCEPT:
				title=n.get_album()
				summary = n.get_commentary()
				access = n.get_access()
				if len(title)>0:
					album=self.picasa.add_album(title,summary=summary,access=access)
					if album is not None:
						self.prepend_album(album)
			n.destroy()	
		else:
			dialog = Gtk.FileChooserDialog(_('Select one or more images to upload to Picasa Web'),
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
				if self.image_dir is None or len(self.image_dir)<=0 or not os.path.exists(self.image_dir):
					self.image_dir = os.getenv('HOME')				
				dialog.destroy()
				if len(filenames)>0:
					self.set_wait_cursor()					
					results = []
					with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
						for filename in filenames:							
							ans = executor.submit(upload_an_image, self.picasa, self.reduce_size, self.max_size, self.reduce_colors, self.album.params['id'], filename, os.path.basename(filename), None)
							results.append(ans.result())
					if len(results)>0:
						sorted(results, key=lambda element: element['index'])
						for element in results:
							self.storeimages.prepend([element['pixbuf'],element['photo_name'],element['photo']])
					self.set_normal_cursor()
					while Gtk.events_pending():
						Gtk.main_iteration()		
			dialog.destroy()
if __name__ == '__main__':
	if os.path.exists('/tmp/picapy.log'):
		os.remove('/tmp/picapy.log')
	logging.basicConfig(filename="/tmp/picapy.log", level=logging.INFO)	
	logging.info("Program started")
	v = Picapy()
	Gtk.main()
	logging.info("Done!")	

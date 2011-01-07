#! /usr/bin/python
# -*- coding: iso-8859-15 -*-
#
__author__="atareao"
__date__ ="$24-abr-2010 12:34:44$"
#
# <one line to give the program"s name and a brief idea of what it does.>
#
# Copyright (C) 2010 Lorenzo Carbonell
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
import gtk
import time
import urllib
import urllib2
import ConfigParser
import os
import gobject
from os import path
from gdata.service import BadAuthentication
import threading
#
from Ini import Ini
from PreferenciasWindow import PreferenciasWindow
from Picasa import Picasa
from NuevoAlbum import NuevoAlbum
from InformacionAlbum import InformacionAlbum
from InformacionImagen import InformacionImagen
from VerImagen import VerImagen
from Progreso import Progreso
from Directorio import filepath
from threading import Thread
import locale
import gettext

APP = 'picapy'
DIR = '/usr/share/locale-langpack'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

class Uploader(Thread):
	def __init__ (self,filename,album,picasa,storeimages):
		Thread.__init__(self)
		self.filename = filename
		self.picasa = picasa
		self.storeimages = storeimages
		self.album = album
		self.status = -1

	def run(self):
		name=os.path.basename(self.filename)[:-4]
		self.photo=self.picasa.add_image(self.album.gphoto_id.text,self.filename,name,name)
		self.status = 0	

	def get_photo(self):
		return self.photo


class DownloaderManager:
	def __init__(self,photos,storeimages):
		self.photos = photos
		self.storeimages = storeimages
		self.downloaders = []
	
	def download(self):
		print len(self.photos)
		p = Progreso(len(self.photos))
		for photo in self.photos:
			print photo.title.text
			print len(self.downloaders)
			while(len(self.downloaders) > 10):
				for down in self.downloaders:
					if down.is_running() == False:
						self.downloaders.remove(down)
			dm=Downloader(photo, self.storeimages)
			dm.start()
			self.downloaders.append(dm)
			p.increase()

class Downloader(Thread):
	def __init__ (self,photo,storeimages):
		Thread.__init__(self)
		self.photo = photo
		self.storeimages = storeimages
		self.running = True

	def run(self):
		f = urllib.urlopen(self.photo.media.thumbnail[0].url)
		data = f.read()
		pbl = gtk.gdk.PixbufLoader()
		pbl.write(data)
		pbuf = pbl.get_pixbuf()
		pbl.close()
		self.storeimages.append([pbuf,self.photo.title.text,self.photo])		
		self.running = False
	
	def is_running(self):
		return self.running

class MainWindow:
	def __init__(self):
		# Con estas dos líneas corregimos el problema de que no exista el directorio de origen
		if os.path.exists(os.path.join(os.getenv("HOME"),".picapy/"))==False:
			os.mkdir(os.path.join(os.getenv("HOME"),".picapy/"))
		filename = os.path.join(os.getenv("HOME"),".picapy/picapy.ini")
		self.ini=Ini(filename)
		error=True
		while error:
			try:
				self.ini.read()	
				self.picasa=Picasa(self.ini.email,self.ini.password)
				error=False
			except BadAuthentication:
				p=PreferenciasWindow(self.ini)
				p.window.run()
				error=True
		#
		self.builder = gtk.Builder()
		self.builder.add_from_file(filepath("picapy.glade"))
		#
		self.window = self.builder.get_object("window")
		self.iconview1 = self.builder.get_object("iconview1")
		self.menu_emergente=self.builder.get_object("menu_emergente")
		self.button1 = self.builder.get_object("button1")
		self.button2 = self.builder.get_object("button2")
		self.button3 = self.builder.get_object("button3")
		self.button4 = self.builder.get_object("button4")
		self.menuitem1 = self.builder.get_object("menuitem1")
		self.menuitem2 = self.builder.get_object("menuitem2")
		self.menuitem3 = self.builder.get_object("menuitem3")
		self.menuitem4 = self.builder.get_object("menuitem4")
		self.menuitem5 = self.builder.get_object("menuitem5")
		self.menuitem6 = self.builder.get_object("menuitem6")
		self.menuitem7 = self.builder.get_object("menuitem7")
		self.menuitem8 = self.builder.get_object("menuitem8")
		self.menuitem9 = self.builder.get_object("menuitem9")
		#
		self.menuitem1.set_label(_('File'))
		self.menuitem2.set_label(_('Edit'))
		self.menuitem3.set_label(_('Information'))
		self.menuitem4.set_label(_('Help'))
		self.menuitem5.set_label(_('Download'))
		self.menuitem6.set_label(_('Copy link to clipboard'))
		self.menuitem7.set_label(_('Copy thumbnail 72x72 link to clipboard'))
		self.menuitem8.set_label(_('Copy thumbnail 144x144 link to clipboard'))
		self.menuitem9.set_label(_('Copy thumbnail 288x288 link to clipboard'))
		self.button1.set_tooltip_text(_('Up'))
		self.button2.set_tooltip_text(_('Add'))
		self.button3.set_tooltip_text(_('Remove'))
		self.button4.set_tooltip_text(_('Exit from Picapy'))
		#
		self.store = gtk.ListStore(gtk.gdk.Pixbuf,str,gobject.TYPE_PYOBJECT)
		self.storeimages = gtk.ListStore(gtk.gdk.Pixbuf,str,gobject.TYPE_PYOBJECT)
		self.iconview1.set_model(self.store)
		self.iconview1.set_pixbuf_column(0)
		self.iconview1.set_text_column(1)
		self.iconview1.set_columns(6)
		#
		self.window.show_all()
		# Magia :P
		self.builder.connect_signals(self)	
		#
		self.inicia_albums()
		self.album=None

	def inicia_images(self):
		modelo = gtk.ListStore(str)
		self.treeview2.set_model(modelo)
		render=gtk.CellRendererText()
		columna=gtk.TreeViewColumn("Imagen",render,text=0)
		self.treeview2.append_column(columna)
		#

	def append_album(self,album):
		pixbuf = gtk.gdk.pixbuf_new_from_file(filepath("gnome-folder.png"))
		album_name=album.title.text
		self.store.append([pixbuf,album_name,album])

	def inicia_albums(self):
		self.store.clear()
		self.albums=[]
		self.albums=self.picasa.get_albums()
		for album in self.albums.entry:
			self.append_album(album)

	def on_informacion_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			if self.album==None:
				selected=self.store.get_iter_from_string(str(items[0][0]))
				i=InformacionAlbum(self.store.get_value(selected,2))
			else:
				selected=self.storeimages.get_iter_from_string(str(items[0][0]))
				i=InformacionImagen(self.storeimages.get_value(selected,2))

	def on_descargar_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			if self.album==None:
				selected=self.store.get_iter_from_string(str(items[0][0]))
				i=InformacionAlbum(self.store.get_value(selected,2))
			else:
				selected=self.storeimages.get_iter_from_string(str(items[0][0]))
				imagen=self.storeimages.get_value(selected,2)
				chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
				if imagen.content.src[imagen.content.src.rfind('/')]>-1:
					fn = imagen.content.src[imagen.content.src.rfind('/')+1:]
					chooser.set_current_name(fn)
				response=chooser.run()
				if response == gtk.RESPONSE_OK:
					filename=chooser.get_filename()
					chooser.destroy()
					self.download_image(imagen.content.src,filename)
				else:
					chooser.destroy()
				
			
	def on_menuitem6_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			clipboard = gtk.clipboard_get()
			selected=self.storeimages.get_iter_from_string(str(items[0][0]))
			imagen=self.storeimages.get_value(selected,2)
			clipboard.set_text(imagen.content.src)
			clipboard.store()

	def on_menuitem7_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			clipboard = gtk.clipboard_get()
			selected=self.storeimages.get_iter_from_string(str(items[0][0]))
			imagen=self.storeimages.get_value(selected,2)
			clipboard.set_text(imagen.media.thumbnail[0].url)
			clipboard.store()

	def on_menuitem8_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			clipboard = gtk.clipboard_get()
			selected=self.storeimages.get_iter_from_string(str(items[0][0]))
			imagen=self.storeimages.get_value(selected,2)
			clipboard.set_text(imagen.media.thumbnail[1].url)
			clipboard.store()

	def on_menuitem9_activated(self,widget):
		items = self.iconview1.get_selected_items()
		if len(items)>0:
			clipboard = gtk.clipboard_get()
			selected=self.storeimages.get_iter_from_string(str(items[0][0]))
			imagen=self.storeimages.get_value(selected,2)
			clipboard.set_text(imagen.media.thumbnail[2].url)
			clipboard.store()
		
	def on_iconview1_button_press_event(self,widget,event):
		if event.button==1 and event.type==gtk.gdk._2BUTTON_PRESS:
			if self.album==None:
				items = self.iconview1.get_selected_items()
				if len(items)>0:
					selected=self.store.get_iter_from_string(str(items[0][0]))
					self.load_images_from_picasa_album(self.store.get_value(selected,2))
			else:
				items = self.iconview1.get_selected_items()
				if len(items)>0:
					selected=self.storeimages.get_iter_from_string(str(items[0][0]))
					image=self.storeimages.get_value(selected,2)
					v = VerImagen(image)
					v.window.run()
					v.window.destroy()
	def on_iconview1_button_release_event(self,widget,event):				
		if event.button == 3:
			items = self.iconview1.get_selected_items()
			if len(items)>0:
				if self.album == None:
					self.menuitem5.set_visible(False)
					self.menuitem6.set_visible(False)
					self.menuitem7.set_visible(False)
					self.menuitem8.set_visible(False)
					self.menuitem9.set_visible(False)
				else:
					self.menuitem5.set_visible(True)
					self.menuitem6.set_visible(True)
					self.menuitem7.set_visible(True)
					self.menuitem8.set_visible(True)
					self.menuitem9.set_visible(True)
				self.menu_emergente.popup( None, None, None, event.button,0)
					

	def load_images_from_picasa_album(self,album):
		self.window.set_title('Picapy | ' + album.title.text)
		photos=self.picasa.get_photos_from_album(album.gphoto_id.text)
		self.storeimages.clear()
		self.iconview1.set_model(self.storeimages)
		# dm = DownloaderManager(photos.entry,self.storeimages)
		# dm.download()
		total = len(photos.entry)
		if total > 0:
			p=Progreso(total)
			for photo in photos.entry:
				while threading.activeCount()>9:
					time.sleep(0.05)
				downloader = Downloader(photo,self.storeimages)
				downloader.start()
				p.increase()
			while threading.activeCount()>1:
				time.sleep(0.05)
			p.close()
		self.iconview1.show()
		self.album=album
		self.button1.set_sensitive(True)
						
	def on_button1_clicked(self,widget):
		self.iconview1.set_model(self.store)		
		self.button1.set_sensitive(False)
		self.album=None
		self.window.set_title('Picapy')
			
	def on_button3_clicked(self,widget):
		if self.album==None:
			items = self.iconview1.get_selected_items()
			if len(items)>0:
				if len(items)>1:
					msg=_('Do you want to delete %s folders?') % str(len(items))
				else:
					msg=_('Do you want to delete this folder?')
				md = gtk.MessageDialog(self.window, 
				gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, 
				gtk.BUTTONS_OK_CANCEL, msg)
				respuesta=md.run()
				if respuesta == gtk.RESPONSE_OK:
					md.destroy()
					p=Progreso(len(items))
					for item in items:
						selected=self.store.get_value(self.store.get_iter_from_string(str(item[0])),2)
						self.picasa.delete_album(selected)
						p.increase()
						self.storeimages.remove(self.storeimages.get_iter_from_string(str(item[0])))
						# modificado ahora cada vez que se elimina una imagen se hace directamente no 
						# es necesario recargar todo el album
						# antes: self.inicia_albums()
				else:
					md.destroy()
		else:
			items = self.iconview1.get_selected_items()
			if len(items)>0:
				if len(items)>1:
					msg=_('Do you want to delete %s images?') % str(len(items))
				else:
					msg=_('Do you want to delete this image?')
				md = gtk.MessageDialog(self.window, 
				gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, 
				gtk.BUTTONS_OK_CANCEL, msg)
				respuesta=md.run()
				if respuesta == gtk.RESPONSE_OK:			
					md.destroy()
					p=Progreso(len(items))
					for item in items:
						image=self.storeimages.get_value(self.storeimages.get_iter_from_string(str(item[0])),2)
						self.picasa.delete_image(image)
						p.increase()
						# modificado ahora cada vez que se elimina una imagen se hace directamente no 
						# es necesario recargar todo el album
						# antes: self.load_images_from_picasa_album(self.album)
						self.storeimages.remove(self.storeimages.get_iter_from_string(str(item[0])))
				else:
					md.destroy()
			
	def on_button2_clicked(self,widget):
		if self.album==None:
			n=NuevoAlbum()
			n.window.run()
			album=n.get_album()
			if len(album)>0:
				album=self.picasa.add_album(album,"Created with Picapy")
				# added: así no tengo que subir todos los album cada vez que creo uno
				self.append_album(album)
				# self.inicia_albums()			
		else:
			dialog = gtk.FileChooserDialog(_('Select one or more images to upload to Picasa Web'),
										   None,
										   gtk.FILE_CHOOSER_ACTION_OPEN,
										   (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
											gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			dialog.set_default_response(gtk.RESPONSE_OK)
			dialog.set_select_multiple(True)
			filter = gtk.FileFilter()
			filter.set_name(_('Imagenes'))
			filter.add_mime_type("image/png")
			filter.add_mime_type("image/jpeg")
			filter.add_mime_type("image/gif")
			filter.add_pattern("*.png")
			filter.add_pattern("*.jpg")
			filter.add_pattern("*.gif")
			dialog.add_filter(filter)
			response = dialog.run()
			if response == gtk.RESPONSE_OK:
				filenames = dialog.get_filenames()
				dialog.destroy()
				p=Progreso(len(filenames)*2)
				pad = []
				for filename in filenames:
					while threading.activeCount()>9:
						time.sleep(0.05)
					uploader = Uploader(filename,self.album,self.picasa,self.storeimages)
					uploader.start()
					pad.append(uploader)
					p.increase()
				while threading.activeCount()>1:
					time.sleep(0.05)
				for uploader in pad:
					while threading.activeCount()>9:
						time.sleep(0.05)
					downloader = Downloader(uploader.get_photo(),self.storeimages)
					downloader.start()
					p.increase()
				while threading.activeCount()>1:
					time.sleep(0.05)
					# borrado: ya no hace falat
					#self.load_images_from_picasa_album(self.album)
			else:
				dialog.destroy()
		
	def on_imagemenuitem5_activate(self,widget):
		exit()

	def on_imagemenuitem6_activate(self,widget):
		p=PreferenciasWindow(self.ini)

	def on_imagemenuitem10_activate(self,widget):
		ad=gtk.AboutDialog()
		ad.set_name('Picapy')
		ad.set_version('1.7.1')
		ad.set_copyright('Copyrignt (c) 2010\nLorenzo Carbonell')
		ad.set_comments(_('An application to manage your images in\nPicasa Web'))
		ad.set_license(_(''+
		'This program is free software: you can redistribute it and/or modify it\n'+
		'under the terms of the GNU General Public License as published by the\n'+
		'Free Software Foundation, either version 3 of the License, or (at your option)\n'+
		'any later version.\n\n'+
		'This program is distributed in the hope that it will be useful, but\n'+
		'WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n'+
		'or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n'+
		'more details.\n\n'+
		'You should have received a copy of the GNU General Public License along with\n'+
		'this program.  If not, see <http://www.gnu.org/licenses/>.'))		
		ad.set_website('http://www.atareao.es')
		ad.set_website_label('http://www.atareao.es')
		ad.set_authors(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_documenters(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_translator_credits('Bernardo Miguel	Savone <bmsavone@gmail.com>\nDario Villar Veres <dario.villar.v@gmail.com>\nLorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>')		
		ad.set_program_name('Picapy')
		ad.set_logo(gtk.gdk.pixbuf_new_from_file(filepath('picapy.svg')))
		ad.run()
		ad.hide()
		
	def on_button4_clicked(self,widget):
		exit()
		
	def on_window_destroy(self,widget):
		exit()

	def download_image(self,url_image,filename):
		opener1 = urllib2.build_opener()
		page1 = opener1.open(url_image)
		my_picture = page1.read()
		#
		fout = open(filename, "wb")
		fout.write(my_picture)
		fout.close()
	
if __name__ == "__main__":
	v = MainWindow()
	gtk.main()

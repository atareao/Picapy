#! /usr/bin/python
# -*- coding: iso-8859-15 -*-
#
__author__='atareao'
__date__ ='$06-jun-2010 12:34:44$'
#
# <one line to give the program's name and a brief idea of what it does.>
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
import gtk
import urllib
from Directorio import filepath
import locale
import gettext

APP = 'picapy'
DIR = '/usr/share/locale-langpack'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

class VerImagen:
	def __init__(self,imagen):
		self.builder = gtk.Builder()
		self.builder.add_from_file(filepath('imagen.glade'))
		#
		self.window = self.builder.get_object('dialog')
		self.button3 = self.builder.get_object('button3')
		self.image1 = self.builder.get_object('image1')
		self.viewport1 = self.builder.get_object('viewport1')
		self.scale=100
		#
		self.window.set_title(_('Picapy'))
		self.button3.set_label(_('Ok'))

		#
		f = urllib.urlopen(imagen.content.src)
		data = f.read()
		pbl = gtk.gdk.PixbufLoader()
		pbl.write(data)
		self.pbuf = pbl.get_pixbuf()
		pbl.close()		
		self.image1.set_from_pixbuf(self.pbuf)
		self.window.show_all()
		# Magia :P
		self.builder.connect_signals(self)	
		#
	def on_button1_clicked(self,widget):
		self.scale=self.scale*1.1
		w=int(self.pbuf.get_width()*self.scale/100)
		h=int(self.pbuf.get_height()*self.scale/100)
		pixbuf=self.pbuf.scale_simple(w,h,gtk.gdk.INTERP_BILINEAR)
		self.image1.set_from_pixbuf(pixbuf)
		self.window.show_all()
		
	def on_button2_clicked(self,widget):
		self.scale=self.scale*.9
		w=int(self.pbuf.get_width()*self.scale/100)
		h=int(self.pbuf.get_height()*self.scale/100)
		pixbuf=self.pbuf.scale_simple(w,h,gtk.gdk.INTERP_BILINEAR)
		self.image1.set_from_pixbuf(pixbuf)
		
	def on_button5_clicked(self,widget):
		self.scale=100
		self.image1.set_from_pixbuf(self.pbuf)
		
	def on_button3_clicked(self,widget):
		self.window.hide()	

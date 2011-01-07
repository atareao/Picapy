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
from Directorio import filepath
import locale
import gettext

APP = 'picapy'
DIR = '/usr/share/locale-langpack'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

class InformacionImagen:
	def __init__(self,imagen):
		self.builder = gtk.Builder()
		self.builder.add_from_file(filepath('imageninformation.glade'))
		#
		self.window = self.builder.get_object('dialog')
		self.entry1 = self.builder.get_object('entry1')
		self.entry2 = self.builder.get_object('entry2')
		self.entry3 = self.builder.get_object('entry3')
		self.entry4 = self.builder.get_object('entry4')
		self.label1 = self.builder.get_object('label1')
		self.label2 = self.builder.get_object('label2')
		self.label3 = self.builder.get_object('label3')
		self.label4 = self.builder.get_object('label4')
		self.label5 = self.builder.get_object('label5')
		self.entry5 = self.builder.get_object('entry5')
		self.label6 = self.builder.get_object('label6')
		self.entry6 = self.builder.get_object('entry6')
		self.label7 = self.builder.get_object('label7')
		self.entry7 = self.builder.get_object('entry7')
		self.button1 = self.builder.get_object('button1')
		self.button2 = self.builder.get_object('button2')
		self.button3 = self.builder.get_object('button3')
		self.button4 = self.builder.get_object('button4')
		self.button5 = self.builder.get_object('button5')
		#
		self.window.set_title(_('Information'))
		self.button1.set_label(_('Ok'))
		self.label1.set_text(_('Album'))
		self.label2.set_text(_('Id'))
		self.label3.set_text(_('Camera'))
		self.label4.set_text(_('Url'))
		self.label5.set_text(_('Thumbnail')+' 72x72')
		self.label6.set_text(_('Thumbnail')+' 144x144')
		self.label7.set_text(_('Thumbnail')+' 288x288')
		#
		self.entry1.set_text(imagen.albumid.text)
		self.entry2.set_text(imagen.gphoto_id.text)
		if imagen.exif.make and imagen.exif.model:
			camera = '%s %s' % (imagen.exif.make.text, imagen.exif.model.text)
		else:
			camera = _('unknown')
		self.entry3.set_text(camera)
		self.entry4.set_text(imagen.content.src)
		self.entry5.set_text(imagen.media.thumbnail[0].url)
		self.entry6.set_text(imagen.media.thumbnail[1].url)
		self.entry7.set_text(imagen.media.thumbnail[2].url)
		self.window.show_all()
		# Magia :P
		self.builder.connect_signals(self)	
		#
		self.album=''

	def on_button1_clicked(self,widget):
		self.window.hide()	

	def on_button2_clicked(self,widget):
		clipboard = gtk.clipboard_get()
		clipboard.set_text(self.entry4.get_text())
		clipboard.store()

	def on_button3_clicked(self,widget):
		clipboard = gtk.clipboard_get()
		clipboard.set_text(self.entry5.get_text())
		clipboard.store()

	def on_button4_clicked(self,widget):
		clipboard = gtk.clipboard_get()
		clipboard.set_text(self.entry6.get_text())
		clipboard.store()

	def on_button5_clicked(self,widget):
		clipboard = gtk.clipboard_get()
		clipboard.set_text(self.entry7.get_text())
		clipboard.store()

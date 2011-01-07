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

class InformacionAlbum:
	def __init__(self,album):
		self.builder = gtk.Builder()
		self.builder.add_from_file(filepath('albuminformation.glade'))
		#
		self.window = self.builder.get_object('dialog')
		self.entry1 = self.builder.get_object('entry1')
		self.entry2 = self.builder.get_object('entry2')
		self.entry3 = self.builder.get_object('entry3')
		self.button1 = self.builder.get_object('button1')
		self.label1 = self.builder.get_object('label1')
		self.label2 = self.builder.get_object('label2')
		self.label3 = self.builder.get_object('label3')
		#
		self.window.set_title(_('Information'))
		self.button1.set_label(_('Ok'))
		self.label1.set_text(_('Album'))
		self.label2.set_text(_('Id'))
		self.label3.set_text(_('Images'))
		#
		self.entry1.set_text(album.title.text)
		self.entry2.set_text(album.gphoto_id.text)
		self.entry3.set_text(album.numphotos.text)
		self.window.show_all()
		# Magia :P
		self.builder.connect_signals(self)	
		#
		self.album=''

	def on_button1_clicked(self,widget):
		self.window.hide()	

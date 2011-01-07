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

class Progreso:
	def __init__(self,max_value):
		self.builder = gtk.Builder()
		self.builder.add_from_file(filepath('progreso.glade'))
		#
		self.window = self.builder.get_object('window')
		self.progressbar = self.builder.get_object('progressbar')
		#
		self.window.set_title(_('Progress'))		
		#
		self.window.show_all()
		# Magia :P
		self.builder.connect_signals(self)
		self.max_value=float(max_value)
		self.value=0.0
		while gtk.events_pending():
			gtk.main_iteration()
		#
	def set_max_value(self,valor):
		self.max_value=valor

	def set_value(self,value):
		if value >=0 and value<=self.max_value:
			self.value = value
			fraction=self.value/self.max_value
			self.progressbar.set_fraction(fraction)
			self.window.map()
			while gtk.events_pending():
				gtk.main_iteration()
			if self.value==self.max_value:
				self.window.hide()		
	def close(self):
		self.window.hide()

	def increase(self):
		self.value+=1.0
		fraction=self.value/self.max_value
		self.progressbar.set_fraction(fraction)
		self.window.map()
		while gtk.events_pending():
			gtk.main_iteration()
		if self.value==self.max_value:
			self.window.hide()

	def decrease(self):
		self.value-=1.0
		fraction=self.value/self.max_value
		self.progressbar.set_fraction(fraction)
		self.window.map()
		while gtk.events_pending():
			gtk.main_iteration()

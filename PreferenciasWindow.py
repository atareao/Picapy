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
from Ini import Ini
from Directorio import filepath
import locale
import gettext

APP = 'picapy'
DIR = '/usr/share/locale-langpack'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

class PreferenciasWindow:
	def __init__(self,ini):
		self.ok=False
		self.ini=ini
		self.ini.read()	
		#
		self.builder = gtk.Builder()
		self.builder.add_from_file(filepath('preferencias.glade'))
		#
		self.window = self.builder.get_object('dialog')
		self.entry1 = self.builder.get_object('entry1')
		self.entry2 = self.builder.get_object('entry2')
		self.button1 = self.builder.get_object('button1')
		self.button2 = self.builder.get_object('button2')
		self.label1 = self.builder.get_object('label1')
		self.label2 = self.builder.get_object('label2')
		#
		self.window.set_title(_('Preferences'))
		self.button1.set_label(_('Ok'))
		self.button2.set_label(_('Cancel'))
		self.label1.set_text(_('Email'))
		self.label2.set_text(_('Password'))		
		#
		self.entry1.set_text(self.ini.email)
		self.entry2.set_text(self.ini.password)
		#
		self.window.show_all()
		# Magia :P
		self.builder.connect_signals(self)	
		#

	def on_button1_clicked(self,widget):
		self.ok=True
		self.ini.set_email(self.entry1.get_text())
		self.ini.set_password(self.entry2.get_text())
		self.ini.write()
		self.window.hide()

	def on_button2_clicked(self,widget):
		self.window.hide()

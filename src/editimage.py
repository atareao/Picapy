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
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import urllib
import comun
import locale
import gettext
import os 

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(comun.APP, comun.LANGDIR)
gettext.textdomain(comun.APP)
_ = gettext.gettext

class EditImage(Gtk.Dialog):
	def __init__(self,parent,image):
		#
		Gtk.Dialog.__init__(self)
		self.set_title(_('Edit Image'))
		self.set_modal(True)
		self.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT)		
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(510,170)
		self.set_resizable(False)
		self.connect('destroy', self.close)
		#
		vbox = Gtk.VBox(spacing = 5)
		vbox.set_border_width(5)
		self.get_content_area().add(vbox)
		#
		frame = Gtk.Frame()
		vbox.pack_start(frame,True,True,0)
		#
		table = Gtk.Table(n_rows = 5, n_columns = 2, homogeneous = False)
		table.set_border_width(5)
		table.set_col_spacings(5)
		table.set_row_spacings(5)
		frame.add(table)
		#
		label1 = Gtk.Label(label=_('Title')+':')
		label1.set_alignment(0,0.5)
		table.attach(label1,0,1,0,1, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry1 = Gtk.Entry()
		self.entry1.set_alignment(0)
		self.entry1.set_width_chars(50)
		self.entry1.set_sensitive(False)
		table.attach(self.entry1,1,2,0,1, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label2 = Gtk.Label(label=_('Summary')+':')
		label2.set_alignment(0,0.5)
		table.attach(label2,0,1,1,2, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry2 = Gtk.Entry()
		self.entry2.set_alignment(0)
		self.entry2.set_width_chars(50)
		table.attach(self.entry2,1,2,1,2, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label3 = Gtk.Label(label=_('Tags')+':')
		label3.set_alignment(0,0.5)
		table.attach(label3,0,1,2,3, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		self.entry3 = Gtk.Entry()
		self.entry3.set_alignment(0)
		self.entry3.set_width_chars(50)
		table.attach(self.entry3,1,2,2,3, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		#
		label4 = Gtk.Label(label=_('Change image')+':')
		label4.set_alignment(0,0.5)
		table.attach(label4,0,1,3,4, xoptions = Gtk.AttachOptions.FILL, yoptions = Gtk.AttachOptions.SHRINK)
		#
		#
		button_save = Gtk.Button()
		button_save.set_size_request(40,40)
		button_save.set_tooltip_text(_('Download'))	
		button_save.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_SAVE,Gtk.IconSize.BUTTON))
		button_save.connect('clicked',self.on_save_activated)
		table.attach(button_save,1,2,3,4, xoptions = Gtk.AttachOptions.SHRINK, yoptions = Gtk.AttachOptions.SHRINK)				
		#
		frame = Gtk.Frame()
		frame.set_size_request(600,400)
		table.attach(frame,0,2,4,5, xoptions = Gtk.AttachOptions.EXPAND, yoptions = Gtk.AttachOptions.SHRINK)
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_size_request(600,400)		
		frame.add(scrolledwindow)
		#
		viewport = Gtk.Viewport()
		viewport.set_size_request(600,400)
		scrolledwindow.add(viewport)
		self.aimage = Gtk.Image()
		viewport.add(self.aimage)
		#
		self.filename = None
		#
		if image != None:
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
			self.filename = '/tmp/editimage_temporal.png'
			if os.path.exists(self.filename):
				os.remove(self.filename)
			f = open(self.filename,'wb')
			f.write(data)
			f.close()
			if pbuf != None:
				pw = pbuf.get_width()
				ph = pbuf.get_height()
				w=550
				h=350
				print(pw,ph)
				perw = pw/w
				perh = ph/h
				print(perw,perh)
				if perw<perh and perh>1:
					w = pw/perh
					h = ph/perh					
					pbuf=pbuf.scale_simple(w,h,GdkPixbuf.InterpType.BILINEAR)
				elif perh<perw and perw>1:
					w = pw/perw
					h = ph/perw
					pbuf=pbuf.scale_simple(w,h,GdkPixbuf.InterpType.BILINEAR)
					
				
				print(w,h)
				print(pbuf)
				self.aimage.set_from_pixbuf(pbuf)
		#
		self.show_all()
	def on_save_activated(self,widget):
		dialog = Gtk.FileChooserDialog(_('Select one images to upload to Picasa Web'),
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
			f = open(self.filename,'rb')
			data = f.read()
			f.close()
			pbl = GdkPixbuf.PixbufLoader()
			pbl.write(data)
			pbuf = pbl.get_pixbuf()
			pbl.close()
			if pbuf != None:
				pw = pbuf.get_width()
				ph = pbuf.get_height()
				w=550
				h=350
				print(pw,ph)
				perw = pw/w
				perh = ph/h
				print(perw,perh)
				if perw<perh and perh>1:
					w = pw/perh
					h = ph/perh					
					pbuf=pbuf.scale_simple(w,h,GdkPixbuf.InterpType.BILINEAR)
				elif perh<perw and perw>1:
					w = pw/perw
					h = ph/perw
					pbuf=pbuf.scale_simple(w,h,GdkPixbuf.InterpType.BILINEAR)
				self.aimage.set_from_pixbuf(pbuf)
		dialog.destroy()		

	def close(self,widget):
		self.destroy()
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
if __name__ == '__main__':
	ia = EditImage(None,None)
	ia.run()

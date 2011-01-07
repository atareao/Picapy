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
import gdata.photos.service
import gdata.media
from gdata.service import BadAuthentication
import gdata.geo
import locale
import gettext

APP = 'picapy'
DIR = '/usr/share/locale-langpack'

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

class Picasa:
	def __init__(self,email,password):
		self.email=email
		self.password=password
		self.gd_client = gdata.photos.service.PhotosService()
		self.gd_client.email = self.email
		self.gd_client.password = self.password
		self.gd_client.source = 'picapy'
		self.gd_client.ProgrammaticLogin()

	def get_albums(self):
		return self.gd_client.GetUserFeed(user=self.email)
	
	def get_photos_from_album(self,album_id):
		photos = self.gd_client.GetFeed('/data/feed/api/user/%s/albumid/%s?kind=photo' % (self.email,album_id))
		return photos


	#def add_album(self,album, summary='Created from Picapy'):
	#	return self.gd_client.InsertAlbum(title=album, summary)
	
	def delete_album(self,album):
		self.gd_client.Delete(album)
	
	def delete_image(self,image):
		self.gd_client.Delete(image)
		
	def add_album(self,title, summary=_('Created with Picapy')):
		album = self.gd_client.InsertAlbum(title, summary)
		return album
		
	def add_image(self,album_id,imagename,title=_('New Photo'),comment=_('Uploaded using Picapy')):
		album_url = '/data/feed/api/user/%s/albumid/%s' % (self.email, album_id)
		if imagename.lower().endswith('png'):
			photo = self.gd_client.InsertPhotoSimple(album_url, title, comment, imagename, content_type='image/png')		
			return photo
		if imagename.lower().endswith('jpg'):
			photo = self.gd_client.InsertPhotoSimple(album_url, title, comment, imagename, content_type='image/jpeg')		
			return photo
		if imagename.lower().endswith('gif'):
			photo = self.gd_client.InsertPhotoSimple(album_url, title, comment, imagename, content_type='image/gif')
			return photo

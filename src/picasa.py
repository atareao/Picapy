#! /usr/bin/python3
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
import gdata.photos.service
import gdata.media
from gdata.service import BadAuthentication
import gdata.geo
import mimetypes
import tempfile
import os
from PIL import Image

'''
Album:

access = None
bytesUsed = None
commentCount = None
commentingEnabled = None
gphoto_id = None
location = None
name = None
nickname = None
numphotos = None
numphotosremaining = None
timestamp = None
user = None

Photo:

albumid = None
checksum = None
client = None
commentCount = None
commentingEnabled = None
geo = <gdata.geo.Where object at 0xb74d52ec>
gphoto_id = None
height = None
media = <gdata.media.Group object at 0xb74d52cc>
position = None
rotation = None
size = None
snippet = None
snippettype = None
tags = <gdata.exif.Tags object at 0xb74d536c>
timestamp = None
truncated = None
version = None
width = None
'''
SUPPORTED_MIMES = ['image/png','image/jpeg','image/gif']
CONVERTED_MIMES = ['image/x-ms-bmp','image/x-icon','image/tiff','image/x-photoshop','x-portable-pixmap']

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
	
	def edit_album(self,album):
		updated_album = self.gd_client.Put(album, album.GetEditLink().href,converter=gdata.photos.AlbumEntryFromString)		
		return updated_album
	
	def delete_image(self,image):
		try:
			self.gd_client.Delete(image)
			return True
		except:
			pass
		return False

	def edit_image(self,image):
		return self.gd_client.UpdatePhotoMetadata(image)
		
	def edit_image_content(self,photo,imagename,size,colors):
		mime = mimetypes.guess_type(imagename)[0]
		print(mime)
		if mime in SUPPORTED_MIMES or mime in CONVERTED_MIMES:
			temp = None
			image =  Image.open(imagename)
			w,h = image.size
			if (size == True and (w>800 or h>800)) or colors == True or mime in CONVERTED_MIMES or mime != 'image/jpeg':
				temp = tempfile.mkstemp(suffix = '.jpg',prefix='picapy_tmp', dir='/tmp')[1]
				print(('converting from %s to %s'%(imagename,temp)))
				if size == True and (w>800 or h>800):
					maximo = 800
					if w > h:
						h = h * maximo/w
						w = maximo
					else:
						w = w * maximo/h
						h = maximo
					image = image.resize([w,h],Image.ANTIALIAS)
					print(('reduced size of %s'%temp))
				if colors == True:
					image = image.convert('P',palette = Image.WEB)
					print(('reduced colors of %s'%temp))
				image.save(temp)
				print(('%s converted!'%temp))
				imagename = temp
				mime = mimetypes.guess_type(imagename)[0]					
		print('########################################################')
		print(mime	)
		res = self.gd_client.UpdatePhotoBlob(photo, imagename, mime)
		if temp != None and os.path.exists(temp):
			os.remove(temp)
			print(('deleted %s'%temp))
		return res
			

	def getContacts(self, user='default'):
		return self.gd_client.GetContacts(user=user) 

	def add_album(self,title, summary, access):
		album = self.gd_client.InsertAlbum(title=title, summary=summary, access=access)
		return album
		
	def add_image_from_pixbuf(self,album_id,pixbuf,title,comment,reduce_size,size,colors):
		temp = tempfile.mkstemp(suffix = '.png',prefix='picapy_tmp', dir='/tmp')[1]
		pixbuf.savev(temp,'png',(),())
		photo = self.add_image(album_id,temp,title,comment,reduce_size,size,colors)
		if temp != None and os.path.exists(temp):
			os.remove(temp)
			print(('deleted %s'%temp))
		return photo

					
	def add_image(self,album_id,imagename,title,comment,reduce_size,size,colors):
		album_url = '/data/feed/api/user/%s/albumid/%s' % (self.email, album_id)
		print(album_url)
		mime = mimetypes.guess_type(imagename)[0]
		print(mime)
		if mime in SUPPORTED_MIMES or mime in CONVERTED_MIMES:
			temp = None
			if reduce_size == True or colors == True or mime in CONVERTED_MIMES:
				image =  Image.open(imagename)
				w,h = image.size
				temp = tempfile.mkstemp(suffix = '.png',prefix='picapy_tmp', dir='/tmp')[1]
				print(('converting from %s to %s'%(imagename,temp)))
				if reduce_size == True and (w>size or h>size):
					maximo = size
					if w > h:
						h = h * maximo/w
						w = maximo
					else:
						w = w * maximo/h
						h = maximo
					image = image.resize([w,h],Image.ANTIALIAS)
					print(('reduced size of %s'%temp))
				if colors == True:
					image = image.convert('P',palette = Image.WEB)
					print(('reduced colors of %s'%temp))
				image.save(temp)
				print(('%s converted!'%temp))
				imagename = temp
				mime = mimetypes.guess_type(imagename)[0]
			try:
				photo = self.gd_client.InsertPhotoSimple(album_url, title, comment, imagename, content_type=mime)		
			except GooglePhotosExceptio as e:
				self.gd_client = gdata.photos.service.PhotosService()
				self.gd_client.ProgrammaticLogin()
				photo = self.gd_client.InsertPhotoSimple(album_url, title, comment, imagename, content_type=mime)		
			if temp != None and os.path.exists(temp):
				os.remove(temp)
				print(('deleted %s'%temp))
			return photo
			
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


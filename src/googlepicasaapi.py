#! /usr/bin/python
# -*- coding: utf-8 -*-
#
#
# googlereaderapi.py
# 
# A python wrapper for the Google Reader
#
# Copyright (C) 2011 Lorenzo Carbonell
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

__author__ = 'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'
__date__ ='$27/10/2012'
__copyright__ = 'Copyright (c) 2012 Lorenzo Carbonell'
__license__ = 'GPLV3'
__url__ = 'http://www.atareao.es'

from gi.repository import Gtk,Gdk
from gi.repository import GdkPixbuf
from services import GoogleService
from logindialog import LoginDialog
from urllib.parse import quote, urlencode, parse_qs
import os
import time
import datetime
import mimetypes
import tempfile
from lxml import etree
import comun
import io
import picasamod

OAUTH2_URL = 'https://accounts.google.com/o/oauth2/'
AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
REDIRECT_URI = 'http://localhost'
CLIENT_ID='419523843851-lcfovgkd216a11tmqccif5jqe2gestne.apps.googleusercontent.com'
CLIENT_SECRET='foXLj8AyMDt8Tsm8wap3GCkc'
SCOPE='https://picasaweb.google.com/data/'
ITEMS_PER_PAGE = 10

LIST_ALBUMS_URL = 'https://picasaweb.google.com/data/feed/api/user/default'#'?alt=json'
CREATE_ALBUMS_URL = 'https://picasaweb.google.com/data/feed/api/user/default'
GET_ALBUM_URL = 'https://picasaweb.google.com/data/entry/api/user/default/albumid/%s'
EDIT_ALBUM_URL = 'https://picasaweb.google.com/data/entry/api/user/default/albumid/%s'
DELETE_ALBUM_URL = 'https://picasaweb.google.com/data/entry/api/user/default/albumid/%s'
LIST_PHOTOS_URL = 'https://picasaweb.google.com/data/feed/api/user/default/albumid/%s'
LIST_PHOTOS_URL2 = 'https://picasaweb.google.com/data/feed/api/user/default/albumid/%s?kind=photo&max-results=20&start-index=%s'
INSERT_PHOTO_URL = 'https://picasaweb.google.com/data/feed/api/user/default/albumid/%s'
DELETE_PHOTO_URL = 'https://picasaweb.google.com/data/entry/api/user/default/albumid/%s/photoid/%s'
EDIT_PHOTO_URL = 'https://picasaweb.google.com/data/media/api/user/default/albumid/%s/photoid/%s'
LIST_TAG_URL = 'https://picasaweb.google.com/data/feed/api/user/default?kind=tag'
ADD_TAG_URL = 'https://picasaweb.google.com/data/feed/api/user/default/albumid/%s/photoid/%s'
LIST_TAG_IN_PHOTO_URL = 'https://picasaweb.google.com/data/feed/api/user/default/albumid/%s/photoid/%s?kind=tag'
DELETE_TAG_IN_PHOTO_URL = 'https://picasaweb.google.com/data/entry/api/user/default/albumid/%s/photoid/%s/tag/%s'
GET_LAST_COMMENTS_URL = 'https://picasaweb.google.com/data/feed/api/user/default?kind=comment&max-results=10'

PUBLIC = 'public'
PRIVATE = 'private'
PROTECTED = 'protected'

SUPPORTED_MIMES = ['image/png','image/jpeg','image/gif']
CONVERTED_MIMES = ['image/vnd.wap.wbmp', 'image/x-ms-bmp', 'image/svg+xml','image/x-portable-anymap','image/tiff', 'image/vnd.microsoft.icon', 'image/x-xbitmap', 'image/pcx', 'image/x-cmu-raster','image/x-xpixmap']

def get_album_id(url):
	pos = url.find('albumid')
	if pos>-1:
		return url[pos:].split('/')[1]
	return None

def get_photo_id(url):
	pos = url.find('photoid')
	if pos>-1:
		return url[pos:].split('/')[1]
	return None

def get_thumbnail_url(url,width):
	elements = url.split('/')
	elements[-2] = 's%s'%width
	elements[-1] = '%s'%(elements[-1])
	return '/'.join(elements)


def get_total_url(url,width):
	elements = url.split('/')
	elements[-1] = 's%s/%s'%(width,elements[-1])
	return '/'.join(elements)

class Tag(object):
	def __init__(self,entry=None):
		self.set_from_entry(entry)
		
	def set_from_entry(self,entry=None):		
		self.params = {}
		self.links = {}
		if entry is None:
			self.xml = None
			self.params['etag'] = None
			self.params['id'] = None
			self.params['published'] = None
			self.params['updated'] = None
			self.params['edited'] = None
			self.params['title'] = None
			self.params['summary'] = None
		else:
			self.xml = entry
			self.params['etag'] = entry.attrib['{http://schemas.google.com/g/2005}etag']
			self.params['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1] if entry.find('{http://www.w3.org/2005/Atom}id') is not None else None
			self.params['published'] = entry.find('{http://www.w3.org/2005/Atom}published').text if entry.find('{http://www.w3.org/2005/Atom}published') is not None else None
			self.params['updated'] = entry.find('{http://www.w3.org/2005/Atom}updated').text if entry.find('{http://www.w3.org/2005/Atom}updated') is not None else None
			self.params['edited'] = entry.find('{http://www.w3.org/2007/app}edited').text if entry.find('{http://www.w3.org/2007/app}edited') is not None else None
			self.params['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text if entry.find('{http://www.w3.org/2005/Atom}title') is not None else None
			self.params['summary'] = entry.find('{http://www.w3.org/2005/Atom}summary').text if entry.find('{http://www.w3.org/2005/Atom}summary') is not None else None
			for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
				self.links[link.attrib['rel']]={'url':link.attrib['href'],'type':link.attrib['type']}

	def get_xml(self):
		return etree.tostring(self.xml,pretty_print=True).decode()

	def __str__(self):
		ans = ''
		for key in self.params.keys():
			ans += '%s -> %s\n'%(key,self.params[key])
		return ans

class Comment(object):
	def __init__(self,entry=None):
		self.set_from_entry(entry)
		
	def set_from_entry(self,entry=None):		
		self.params = {}
		self.links = {}
		if entry is None:
			self.xml = None
			self.params['etag'] = None
			self.params['id'] = None
			self.params['album'] = None
			self.params['photo'] = None
			self.params['published'] = None
			self.params['updated'] = None
			self.params['edited'] = None
			self.params['title'] = None
			self.params['content'] = None
		else:
			self.xml = entry
			self.params['etag'] = entry.attrib['{http://schemas.google.com/g/2005}etag']
			self.params['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1] if entry.find('{http://www.w3.org/2005/Atom}id') is not None else None
			self.params['album'] = get_album_id(entry.find('{http://www.w3.org/2005/Atom}id').text) if entry.find('{http://www.w3.org/2005/Atom}id') is not None else None
			self.params['photo'] = get_photo_id(entry.find('{http://www.w3.org/2005/Atom}id').text) if entry.find('{http://www.w3.org/2005/Atom}id') is not None else None
			self.params['published'] = entry.find('{http://www.w3.org/2005/Atom}published').text if entry.find('{http://www.w3.org/2005/Atom}published') is not None else None
			self.params['updated'] = entry.find('{http://www.w3.org/2005/Atom}updated').text if entry.find('{http://www.w3.org/2005/Atom}updated') is not None else None
			self.params['edited'] = entry.find('{http://www.w3.org/2007/app}edited').text if entry.find('{http://www.w3.org/2007/app}edited') is not None else None
			self.params['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text if entry.find('{http://www.w3.org/2005/Atom}title') is not None else None
			self.params['content'] = entry.find('{http://www.w3.org/2005/Atom}content').text if entry.find('{http://www.w3.org/2005/Atom}content') is not None else None
			for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
				self.links[link.attrib['rel']]={'url':link.attrib['href'],'type':link.attrib['type']}

	def get_xml(self):
		return etree.tostring(self.xml,pretty_print=True).decode()

	def __str__(self):
		ans = ''
		for key in self.params.keys():
			ans += '%s -> %s\n'%(key,self.params[key])
		return ans
			
class Photo(object):
	def __init__(self,entry=None):
		self.set_from_entry(entry)
		
	def set_from_entry(self,entry=None):		
		self.params = {}
		self.links = {}
		self.thumbnails = []
		if entry is not None:
			self.xml = entry
			self.params['etag'] = entry.attrib['{http://schemas.google.com/g/2005}etag']
			self.params['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1] if entry.find('{http://www.w3.org/2005/Atom}id') is not None else None
			self.params['published'] = entry.find('{http://www.w3.org/2005/Atom}published').text if entry.find('{http://www.w3.org/2005/Atom}published') is not None else None
			self.params['updated'] = entry.find('{http://www.w3.org/2005/Atom}updated').text if entry.find('{http://www.w3.org/2005/Atom}updated') is not None else None
			self.params['edited'] = entry.find('{http://www.w3.org/2007/app}edited').text if entry.find('{http://www.w3.org/2007/app}edited') is not None else None
			self.params['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text if entry.find('{http://www.w3.org/2005/Atom}title') is not None else None
			self.params['summary'] = entry.find('{http://www.w3.org/2005/Atom}summary').text if entry.find('{http://www.w3.org/2005/Atom}summary') is not None else None
			self.params['content'] = entry.find('{http://www.w3.org/2005/Atom}content').attrib['src'] if entry.find('{http://www.w3.org/2005/Atom}content') is not None else None			
			self.params['albumid'] = entry.find('{http://schemas.google.com/photos/2007}albumid').text if entry.find('{http://schemas.google.com/photos/2007}albumid') is not None else None
			self.params['access'] = entry.find('{http://schemas.google.com/photos/2007}access').text if entry.find('{http://schemas.google.com/photos/2007}access') is not None else None
			self.params['width'] = entry.find('{http://schemas.google.com/photos/2007}width').text if entry.find('{http://schemas.google.com/photos/2007}width') is not None else None
			self.params['height'] = entry.find('{http://schemas.google.com/photos/2007}height').text if entry.find('{http://schemas.google.com/photos/2007}height') is not None else None
			self.params['size'] = entry.find('{http://schemas.google.com/photos/2007}size').text if entry.find('{http://schemas.google.com/photos/2007}size') is not None else None
			self.params['timestamp'] = entry.find('{http://schemas.google.com/photos/2007}timestamp').text if entry.find('{http://schemas.google.com/photos/2007}timestamp') is not None else None
			self.params['url'] = get_total_url(self.params['content'],self.params['width'])
			self.params['thumbnail2'] = get_total_url(self.params['content'],72)
			for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
				self.links[link.attrib['rel']]={'url':link.attrib['href'],'type':link.attrib['type']}
			group = entry.find('{http://search.yahoo.com/mrss/}group')
			if group is not None:
				self.params['content'] = group.find('{http://search.yahoo.com/mrss/}content').attrib['url'] if group.find('{http://search.yahoo.com/mrss/}content') is not None else None
				self.params['keywords'] = group.find('{http://search.yahoo.com/mrss/}keywords').text if group.find('{http://search.yahoo.com/mrss/}keywords') is not None else None
				for th in group.findall('{http://search.yahoo.com/mrss/}thumbnail'):
					thumbnail = {'url':th.attrib['url'],'height':th.attrib['height'],'width':th.attrib['width']}
					self.thumbnails.append(thumbnail)
			else:
				self.params['content'] = None
				self.params['keywords'] = None
		else:
			self.xml = None
			self.params['etag'] = None
			self.params['id'] = None
			self.params['published'] = None
			self.params['updated'] = None
			self.params['edited'] = None
			self.params['title'] = None
			self.params['summary'] = None
			self.params['content'] = None
			self.params['albumid'] = None
			self.params['access'] = None
			self.params['width'] = None
			self.params['height'] = None
			self.params['size'] = None
			self.params['timestamp'] = None
			self.params['content'] = None
			self.params['keywords'] = None

	def get_xml(self):
		return etree.tostring(self.xml,pretty_print=True).decode()

	def __str__(self):
		ans = ''
		for key in self.params.keys():
			ans += '%s -> %s\n'%(key,self.params[key])
		for th in self.thumbnails:
			ans += 'thumbnail (%sx%s): %s\n'%(th['width'],th['height'],th['url'])
		return ans

	def __lt__(self, other):
		return self.params['published']  > other.params['published'] 
	
	def __gt__(self, other):
		return self.params['published']  < other.params['published'] 
		
class Album(object):
	def __init__(self,entry=None):
		self.set_from_entry(entry)
	def set_from_entry(self,entry=None):
		self.params = {}
		self.links = {}
		if entry is not None:
			self.xml = entry
			self.params['etag'] = entry.attrib['{http://schemas.google.com/g/2005}etag']
			self.params['id'] = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1] if entry.find('{http://www.w3.org/2005/Atom}id') is not None else None
			self.params['published'] = entry.find('{http://www.w3.org/2005/Atom}published').text if entry.find('{http://www.w3.org/2005/Atom}published') is not None else None
			self.params['updated'] = entry.find('{http://www.w3.org/2005/Atom}updated').text if entry.find('{http://www.w3.org/2005/Atom}updated') is not None else None
			self.params['edited'] = entry.find('{http://www.w3.org/2007/app}edited').text if entry.find('{http://www.w3.org/2007/app}edited') is not None else None
			self.params['title'] = entry.find('{http://www.w3.org/2005/Atom}title').text if entry.find('{http://www.w3.org/2005/Atom}title') is not None else None
			self.params['summary'] = entry.find('{http://www.w3.org/2005/Atom}summary').text if entry.find('{http://www.w3.org/2005/Atom}summary') is not None else None
			self.params['rights'] = entry.find('{http://www.w3.org/2005/Atom}rights').text if entry.find('{http://www.w3.org/2005/Atom}rights') is not None else None
			self.params['name'] = entry.find('{http://schemas.google.com/photos/2007}name').text if entry.find('{http://schemas.google.com/photos/2007}name') is not None else None
			self.params['access'] = entry.find('{http://schemas.google.com/photos/2007}access').text if entry.find('{http://schemas.google.com/photos/2007}access') is not None else None
			self.params['timestamp'] = entry.find('{http://schemas.google.com/photos/2007}timestamp').text if entry.find('{http://schemas.google.com/photos/2007}timestamp') is not None else None
			self.params['numphotos'] = entry.find('{http://schemas.google.com/photos/2007}numphotos').text if entry.find('{http://schemas.google.com/photos/2007}numphotos') is not None else None
			self.params['numphotosremaining'] = entry.find('{http://schemas.google.com/photos/2007}numphotosremaining').text if entry.find('{http://schemas.google.com/photos/2007}numphotosremaining') is not None else None
			self.params['bytesUsed'] = entry.find('{http://schemas.google.com/photos/2007}bytesUsed').text if entry.find('{http://schemas.google.com/photos/2007}bytesUsed') is not None else None
			self.params['location'] = entry.find('{http://schemas.google.com/photos/2007}location').text if entry.find('{http://schemas.google.com/photos/2007}location') is not None else None
			self.params['user'] = entry.find('{http://schemas.google.com/photos/2007}user').text if entry.find('{http://schemas.google.com/photos/2007}user') is not None else None
			self.params['nickname'] = entry.find('{http://schemas.google.com/photos/2007}nickname').text if entry.find('{http://schemas.google.com/photos/2007}nickname') is not None else None
			for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
				self.links[link.attrib['rel']]={'url':link.attrib['href'],'type':link.attrib['type']}			
			group = entry.find('{http://search.yahoo.com/mrss/}group')
			if group is not None:
				self.params['content'] = group.find('{http://search.yahoo.com/mrss/}content').attrib['url'] if group.find('{http://search.yahoo.com/mrss/}content') is not None else None
				self.params['thumbnail'] = group.find('{http://search.yahoo.com/mrss/}thumbnail').attrib['url'] if group.find('{http://search.yahoo.com/mrss/}thumbnail') is not None else None
				self.params['thumbnail2'] = get_thumbnail_url(self.params['thumbnail'],100) if self.params['thumbnail'] is not None else None
				self.params['keywords'] = group.find('{http://search.yahoo.com/mrss/}keywords').text if group.find('{http://search.yahoo.com/mrss/}keywords') is not None else None
			else:
				self.params['content'] = None
				self.params['thumbnail'] = None
				self.params['thumbnail2'] = None
				self.params['keywords'] = None
		else:
			self.xml = None
			self.params['etag'] = None
			self.params['id'] = None
			self.params['published'] = None
			self.params['updated'] = None
			self.params['edited'] = None
			self.params['title'] = None
			self.params['summary'] = None
			self.params['rights'] = None
			self.params['name'] = None
			self.params['access'] = None
			self.params['timestamp'] = None
			self.params['numphotos'] = None
			self.params['numphotosremaining'] = None
			self.params['bytesUsed'] = None
			self.params['location'] = None
			self.params['user'] = None
			self.params['nickname'] = None
			self.params['content'] = None
			self.params['thumbnail'] = None
			self.params['keywords'] = None

	def get_xml(self):
		return etree.tostring(self.xml,pretty_print=True).decode()
			
	def __str__(self):
		ans = ''
		for key in self.params.keys():
			ans += '%s -> %s\n'%(key,self.params[key])
		return ans
		
	def __lt__(self, other):
		return self.params['published']  > other.params['published'] 
	
	def __gt__(self, other):
		return self.params['published']  < other.params['published'] 
			
class Picasa(GoogleService):			
	def __init__(self,token_file):
		GoogleService.__init__(self,auth_url=AUTH_URL,token_url=TOKEN_URL,redirect_uri=REDIRECT_URI,scope=SCOPE,client_id=CLIENT_ID,client_secret=CLIENT_SECRET,token_file=comun.TOKEN_FILE)

	def __do_request(self,method,url,addheaders=None,data=None,params=None,first=True,files=None):
		headers ={'Authorization':'OAuth %s'%self.access_token,'GData-Version':'2'}
		if addheaders:
			headers.update(addheaders)
		if data:
			if params:
				response = self.session.request(method,url,data=data,headers=headers,params=params,files=files)
			else:
				response = self.session.request(method,url,data=data,headers=headers,files=files)
		else:
			if params:
				response = self.session.request(method,url,headers=headers,params=params,files=files)
			else:		
				response = self.session.request(method,url,headers=headers,files=files)
		print(response,response.status_code)
		if response.status_code == 200 or response.status_code == 201:
			return response
		elif (response.status_code == 401 or response.status_code == 403) and first:
			ans = self.do_refresh_authorization()
			if ans:
				return self.__do_request(method,url,addheaders,data,params,first=False)
		return None

	def get_last_comments(self):
		comments = []
		response = self.__do_request('GET',GET_LAST_COMMENTS_URL)
		if response and response.text:
			answer = response.text.encode()
			root = etree.fromstring(answer)
			entries = root.findall('{http://www.w3.org/2005/Atom}entry')
			for entry in entries:
				comments.append(Comment(entry))
		return comments
			
	def get_tags(self):
		tags = []
		response = self.__do_request('GET',LIST_TAG_URL)		
		if response and response.text:
			answer = response.text.encode()
			root = etree.fromstring(answer)
			entries = root.findall('{http://www.w3.org/2005/Atom}entry')
			for entry in entries:
				tag = Tag(entry)
				tags.append(tag)
		return tags
	
	def get_tags_in_photo(self,album_id,photo_id):
		tags = []
		response = self.__do_request('GET',LIST_TAG_IN_PHOTO_URL%(album_id,photo_id))
		if response and response.text:
			answer = response.text.encode()
			root = etree.fromstring(answer)
			entries = root.findall('{http://www.w3.org/2005/Atom}entry')
			for entry in entries:
				tag = Tag(entry)
				tags.append(tag)
		return tags

	def get_albums(self):
		albums = []
		params = {'max-results':100000}
		response = self.__do_request('GET',LIST_ALBUMS_URL,params=params)		
		if response and response.text:
			answer = response.text.encode()
			root = etree.fromstring(answer)
			entries = root.findall('{http://www.w3.org/2005/Atom}entry')
			for entry in entries:
				album = Album(entry)
				albums.append(album)				
		return sorted(albums)

	def get_photo(self,album_id,photo_id):
		photos = self.get_photos(album_id)
		for photo in photos:
			if photo.params['id'] == photo_id:
				return photo
		return None
		
	def get_album(self,id):
		response = self.__do_request('GET',GET_ALBUM_URL%id)
		if response and response.text:
			return Album(etree.fromstring(response.text.encode()))
		return None
	def add_tag(self,album_id,photo_id,title):
		xml = '<entry xmlns="http://www.w3.org/2005/Atom">\r\n'
		xml += '<title>%s</title>\r\n'%(title)
		xml += '<category scheme="http://schemas.google.com/g/2005#kind" '
		xml += 'term="http://schemas.google.com/photos/2007#tag"/>\r\n'
		xml += '</entry>'
		xml = xml.encode('utf-8')
		response = self.__do_request('POST',ADD_TAG_URL%(album_id,photo_id),addheaders={'Content-type':'application/atom+xml'},data=xml)	
		if response and response.status_code == 201 and response.text:			
			return Tag(etree.fromstring(response.text.encode()))
		return None
		
	def add_album(self,title,summary=None,access=PUBLIC,location=None,keywords = None):
		xml = """<entry xmlns='http://www.w3.org/2005/Atom'
		xmlns:media='http://search.yahoo.com/mrss/'
		xmlns:gphoto='http://schemas.google.com/photos/2007'>
		<title type='text'>%s</title>"""%(title)
		if summary is not None:
			xml +="<summary type='text'>%s</summary>"%(summary)
		if location is not None:
			xml +="<gphoto:location>%s</gphoto:location>"%(location)
		xml += "<gphoto:access>%s</gphoto:access>"%(access)
		xml += "<gphoto:timestamp>%s</gphoto:timestamp>"%(int(time.time()*1000))
		if keywords is not None:
			xml += "<media:group><media:keywords>%s</media:keywords></media:group>"%(keywords)
		xml += """<category scheme='http://schemas.google.com/g/2005#kind'
		term='http://schemas.google.com/photos/2007#album'></category>
		</entry>"""
		xml = xml.encode('utf-8')
		response = self.__do_request('POST',CREATE_ALBUMS_URL,addheaders={'Content-type':'application/atom+xml'},data=xml)	
		if response and response.status_code == 201 and response.text:			
			return Album(etree.fromstring(response.text.encode()))
		return None
	def delete_album(self,album):
		return self.__delete_album(album.params['id'])
	def __delete_album(self,id):
		response = self.__do_request('DELETE',DELETE_ALBUM_URL%id,addheaders={'If-match':'*'})
		if response and response.status_code == 200 :
			return True
		return False	
	def edit_album(self,album):
		id = album.params['id']
		title = album.params['title']
		summary = album.params['summary']
		access = album.params['rights']
		return self.__edit_album(id,title=title,summary=summary,access=access)
	def __edit_album(self,id,title=None,summary=None,location=None,access=PUBLIC,keywords=None):
		album = self.get_album(id)
		if album is not None:
			xml = etree.tostring(album.xml).decode()
			if title is not None:
				xml = xml.replace('<title>%s</title>'%(album.params['title']),'<title>%s</title>'%(title))
				xml = xml.replace("<media:title type='plain'>%s</media:title>"%(album.params['title']),"<media:title type='plain'>%s</media:title>"%(title))
			if summary is not None:
				if album.params['summary'] is None:
					xml = xml.replace('<summary/>','<summary>%s</summary>'%(summary))
				else:
					xml = xml.replace('<summary>%s</summary>'%(album.params['summary']),'<summary>%s</summary>'%(summary))
			if location is not None:
				if album.params['location'] is None:
					xml = xml.replace('<gphoto:location/>','<gphoto:location>%s</gphoto:location>'%(location))
				else:
					xml = xml.replace('<gphoto:location>%s</gphoto:location>'%(album.params['keywords']),'<gphoto:location>%s</gphoto:location>'%(location))
			xml = xml.replace('<rights>%s</rights>'%(album.params['access']),'<rights>%s</rights>'%(access))
			xml = xml.replace('<gphoto:access>%s</gphoto:access>'%(album.params['access']),'<gphoto:access>%s</gphoto:access>'%(access))
			'''
			if access == PUBLIC:
				xml = xml.replace('<gphoto:access>%s</gphoto:access>'%(album.params['access']),'<gphoto:access>public</gphoto:access>')
			else:
				xml = xml.replace('<gphoto:access>%s</gphoto:access>'%(album.params['access']),'<gphoto:access>private</gphoto:access>')
			'''
			if keywords is not None:
				if album.params['keywords'] is None:
					xml = xml.replace('<media:keywords/>','<media:keywords>%s</media:keywords>'%(keywords))
				else:
					xml = xml.replace('<media:keywords>%s</media:keywords>'%(album.params['keywords']),'<media:keywords>%s</media:keywords>'%(keywords))
			response = self.__do_request('PUT',EDIT_ALBUM_URL%id,addheaders={'Content-type':'application/atom+xml','If-match':'*'},data=xml)
			if response and response.status_code == 200 and response.text:			
				return Album(etree.fromstring(response.text.encode()))
			else:
				print(response.status.code)
		return None	
	
	def get_photos_in_page(self,album_id,page):
		photos = []
		start_index = (page-1)*10+1
		response = self.__do_request('GET',LIST_PHOTOS_URL2%(album_id,start_index))
		if response and response.text:
			print(response.text)
			answer = response.text.encode()
			root = etree.fromstring(answer)
			entries = root.findall('{http://www.w3.org/2005/Atom}entry')
			for entry in entries:
				photo = Photo(entry)
				photos.append(photo)
		return photos
		
	def get_photos(self,album_id):
		photos = []
		params = {'max-results':1000}
		response = self.__do_request('GET',LIST_PHOTOS_URL%album_id,params=params)		
		if response and response.text:
			answer = response.text.encode()
			root = etree.fromstring(answer)
			entries = root.findall('{http://www.w3.org/2005/Atom}entry')
			for entry in entries:
				photo = Photo(entry)
				photos.append(photo)
		return sorted(photos)
		
	def edit_photo_from_id(self,album_id,photo_id,afile,filename=None,caption=None):
		photo = self.get_photo(album_id,photo_id)
		if photo:
			return self.edit_photo(album_id,photo,afile,filename,caption)
		return None
		
	def edit_photo(self,album_id,photo,afile,filename=None,caption=None):		
		mime = mimetypes.guess_type(afile)[0]
		content_type = ('Content-Type: %s'%(mime)).encode('utf-8')
		print(afile)
		afilee = open(afile,'rb')
		data = afilee.read()
		afilee.close()		
		xml = etree.tostring(photo.xml).decode()	
		if filename is not None:
			xml = xml.replace('<title>%s</title>'%(photo.params['title']),'<title>%s</title>'%(filename))
			xml = xml.replace("<media:title type='plain'>%s</media:title>"%(photo.params['title']),"<media:title type='plain'>%s</media:title>"%(filename))
		if caption is not None:
			if photo.params['summary'] is None:
				xml = xml.replace('<summary/>','<summary>%s</summary>'%(caption))
			else:
				xml = xml.replace('<summary>%s</summary>'%(photo.params['summary']),'<summary>%s</summary>'%(caption))
		body = io.BytesIO()
		body.write(b"Media multipart posting\r\n")
		body.write(b"--END_OF_PART\r\n")
		body.write(b"Content-Type: application/atom+xml\r\n\r\n")
		body.write(xml.encode('utf-8'))
		body.write(b"\r\n--END_OF_PART\r\n")
		body.write(content_type)
		body.write(b" MIME-Version: 1.0\r\n\r\n")
		body.write(data)
		body.write(b"\r\n--END_OF_PART--")
		body = body.getvalue()
		url = EDIT_PHOTO_URL%(album_id,photo.params['id'])
		response = self.__do_request('PUT',url,addheaders={'Content-type':'multipart/related; boundary="END_OF_PART"','Content-length':str(len(body)),'MIME-version':'1.0','If-Match':'*'},data=body)
		if response and response.status_code == 200 and response.text:
			return Photo(etree.fromstring(response.text.encode()))
		return None
	
	def add_image_from_pixbuf(self,album_id,pixbuf,title,comment,reduce_size,size,colors):
		temp = tempfile.mkstemp(suffix = '.png',prefix='picapy_tmp', dir='/tmp')[1]
		pixbuf.savev(temp,'png',(),())
		photo = self.add_image(album_id,temp,title,comment,reduce_size,size,colors)
		if temp != None and os.path.exists(temp):
			os.remove(temp)
		return photo		
	
	def add_image(self,album_id,imagename,title,comment,reduce_size=False,size=800,colors=False):	
		mime = mimetypes.guess_type(imagename)[0]
		if mime in SUPPORTED_MIMES or mime in CONVERTED_MIMES:
			temp = None
			if reduce_size == True or colors == True or mime in CONVERTED_MIMES:
				pixbuf =  GdkPixbuf.Pixbuf.new_from_file(imagename)
				temp = tempfile.mkstemp(suffix = '.png',prefix='picapy_tmp', dir='/tmp')[1]			
				if reduce_size == True:				
					pixbuf = picasamod.scale_pixbuf(pixbuf,size)
					print('reduced size of %s'%temp)
				if colors == True:
					pixbuf = picasamod.grayscale_pixbuf(pixbuf)
					print(('reduced colors of %s'%temp))
				pixbuf.savev(temp,'png',[],[])
				print(('%s converted!'%temp))
				imagename = temp
			ans =self.add_photo(album_id,afile=imagename,filename=title,caption=comment)
			print('The ans %s'%ans)
			if temp is not None and os.path.exists(temp):
				os.remove(temp)
			if ans:
				return ans
		return None
		
	def add_photo(self,album_id,afile,filename=None,caption=None):		
		if filename is None:
			filename = afile.split('/')[-1]
		filename = ('<title>%s</title>\r\n'%(filename))
		if caption is None:
			caption =  afile.split('/')[-1].split('.')[0]
		caption = ('<summary>%s</summary>\r\n'%(caption))
		body_text = io.StringIO()
		body_text.write('Media multipart posting\r\n')
		body_text.write('--END_OF_PART\r\n')
		body_text.write('Content-Type: application/atom+xml\r\n\r\n')
		body_text.write('<entry xmlns="http://www.w3.org/2005/Atom">\r\n')
		body_text.write(filename)
		body_text.write(caption)
		body_text.write('<category scheme="http://schemas.google.com/g/2005#kind" ')
		body_text.write('term="http://schemas.google.com/photos/2007#photo"/>\r\n')
		body_text.write('</entry>\r\n\r\n')
		body_text.write('--END_OF_PART\r\n')
		body_text.write('Content-Type: %s\r\n'%(mimetypes.guess_type(afile)[0]))
		body_text.write('MIME-Version: 1.0\r\n\r\n')
		body = io.BytesIO()
		body.write(body_text.getvalue().encode('utf-8'))
		afilee = open(afile,'rb')
		data = afilee.read()
		afilee.close()
		body.write(data)
		body.write('\r\n--END_OF_PART--'.encode('utf-8'))
		body = body.getvalue()
		response = self.__do_request('POST',INSERT_PHOTO_URL%album_id,addheaders={'Content-type':'multipart/related; boundary="END_OF_PART"','Content-length':str(len(body)),'MIME-version':'1.0'},data=body)
		if response and response.status_code == 201 and response.text:
			return Photo(etree.fromstring(response.text.encode()))
		return None

	def delete_tag_in_photo(self,album_id,photo_id,tag_id):
		response = self.__do_request('DELETE',DELETE_TAG_IN_PHOTO_URL%(album_id,photo_id,tag_id))
		if response and (response.status_code == 200 or response.status_code == 404):
			return True
		return False
	def delete_photo(self,album,photo):
		return self.__delete_photo(album.params['id'],photo.params['id'])
	def __delete_photo(self,album_id,photo_id):
		response = self.__do_request('DELETE',DELETE_PHOTO_URL%(album_id,photo_id),addheaders={'If-match':'*'})
		if response and response.status_code == 200 :
			return True
		return False
		
if __name__=='__main__' :
	pi = Picasa(token_file = comun.TOKEN_FILE)
	print(pi.do_refresh_authorization())
	print(pi.get_albums()[0])
	#pi.do_revoke_authorization() 
	ans = pi.add_photo('5803966623150991473',"/home/atareao/Imágenes/G'MIC para GIMP 64 bits - 1.5.6.1_031.png")	
	print(ans)
	'''
	
	if (pi.access_token == None or pi.refresh_token == None):
		authorize_url = pi.get_authorize_url()
		print(authorize_url)
		ld = LoginDialog(authorize_url)
		ld.run()
		pi.get_authorization(ld.code)
		ld.destroy()
	#albums = pi.get_albums()
	#print(pi.create_album('adasfadfdafda','tesfdafdafdafdat',access=PRIVATE))
	#pi.add_album(id = '5803966623150991473',title='en un lugar')
	#print(pi.get_album('5802582323893992801'))
	#print(pi.edit_album('5802582323893992801',title='fdafdafdafdafdsafdasfdfdasfdafdasfd',summary = 'This is a test', location = 'Valencia',access_public=False,keywords='1,2,3,4'))
	#print(pi.delete_album('5802605835265135169'))
	#photos = pi.get_photos('5432806850630397153')
	'''
	'''
	ans = pi.add_photo('5803966623150991473','/home/atareao/Imágenes/G'MIC para GIMP 64 bits - 1.5.6.1_031.png')	
	if ans:
		print(ans)
		print(etree.tostring(ans.xml).decode())
		f = open('/tmp/salida.sal','w')
		f.write(etree.tostring(ans.xml,pretty_print=True).decode())
		f.close()
	ans = pi.edit_photo_from_id('5811515891101718113','5811515970947568658','/home/atareao/Imágenes/0028_Tribler 6.0.0.png')
	if ans:
		print(ans)

	tags = pi.get_tags_in_photo('5803966623150991473','5804032291729118658')
	for tag in tags:
		print(tag)
		#print(tag.get_xml())
	for comment in pi.get_last_comments():
		print(comment)
		#print(comment.get_xml())
	'''
	#print(pi.add_album('otra prueba','otra prueba mas',access=PRIVATE))
	#print(pi.edit_album(id='5804064415930256545',access=PRIVATE))
	#ans = pi.add_photo('5803966623150991473','/home/atareao/Imágenes/0029_Tribler 6.0.0.png')	
	'''
	ans = pi.add_image('5803966623150991473','/home/atareao/Imágenes/0029_Tribler 6.0.0.png','titulo','comentario',reduce_size=True,size=300,colors=True)
	if ans:
		print(ans)
	
	ans = pi.get_photo('5803966623150991473','5804247132197469602')
	if ans:
		print(ans)
	'''
	print(pi.get_album('5426716353448836273'))
	#print(pi.get_photos_in_page('5803966623150991473',1))
	ans = pi.edit_photo_from_id('5811515891101718113','5811517614627182034','/home/atareao/Imágenes/0028_Tribler 6.0.0.png')
	if ans:
		print(ans)
	
	exit(0)


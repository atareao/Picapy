#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of picapy
#
# Copyright (C) 2010-2016 Lorenzo Carbonell

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

import gi
try:
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import Gdk
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
CLIENT_ID = '419523843851-lcfovgkd216a11tmqccif5jqe2gestne.\
apps.googleusercontent.com'
CLIENT_SECRET = 'foXLj8AyMDt8Tsm8wap3GCkc'
SCOPE = 'https://picasaweb.google.com/data/'
ITEMS_PER_PAGE = 10

LIST_ALBUMS_URL = SCOPE + 'feed/api/user/default'
CREATE_ALBUMS_URL = SCOPE + 'feed/api/user/default'
GET_ALBUM_URL = SCOPE + 'entry/api/user/default/albumid/%s'
EDIT_ALBUM_URL = SCOPE + 'entry/api/user/default/albumid/%s'
DELETE_ALBUM_URL = SCOPE + 'entry/api/user/default/albumid/%s'
LIST_PHOTOS_URL = SCOPE + 'feed/api/user/default/albumid/%s'
LIST_PHOTOS_URL2 = SCOPE + 'feed/api/user/default/albumid/\
%s?kind=photo&max-results=20&start-index=%s'
INSERT_PHOTO_URL = SCOPE + 'feed/api/user/default/albumid/%s'
DELETE_PHOTO_URL = SCOPE + 'entry/api/user/default/albumid/%s/photoid/%s'
EDIT_PHOTO_URL = SCOPE + 'media/api/user/default/albumid/%s/photoid/%s'
LIST_TAG_URL = SCOPE + 'feed/api/user/default?kind=tag'
ADD_TAG_URL = SCOPE + 'feed/api/user/default/albumid/%s/photoid/%s'
LIST_TAG_IN_PHOTO_URL = SCOPE + 'feed/api/user/default/albumid/\
%s/photoid/%s?kind=tag'
DELETE_TAG_IN_PHOTO_URL = SCOPE + 'entry/api/user/default/albumid/\
%s/photoid/%s/tag/%s'
GET_LAST_COMMENTS_URL = SCOPE + 'feed/api/user/default?kind=\
comment&max-results=10'
ATOM = '{http://www.w3.org/2005/Atom}'
ATOM2 = '{http://www.w3.org/2007/Atom}'
PHOTOS = '{http://schemas.google.com/photos/2007}'

PUBLIC = 'public'
PRIVATE = 'private'
PROTECTED = 'protected'

SUPPORTED_MIMES = ['image/png', 'image/jpeg', 'image/gif']
CONVERTED_MIMES = [
    'image/vnd.wap.wbmp', 'image/x-ms-bmp', 'image/svg+xml',
    'image/x-portable-anymap', 'image/tiff', 'image/vnd.microsoft.icon',
    'image/x-xbitmap', 'image/pcx', 'image/x-cmu-raster', 'image/x-xpixmap']


def get_album_id(url):
    pos = url.find('albumid')
    if pos > -1:
        return url[pos:].split('/')[1]
    return None


def get_photo_id(url):
    pos = url.find('photoid')
    if pos > -1:
        return url[pos:].split('/')[1]
    return None


def get_thumbnail_url(url, width):
    elements = url.split('/')
    elements[-2] = 's%s' % width
    elements[-1] = '%s' % (elements[-1])
    return '/'.join(elements)


def get_total_url(url, width):
    elements = url.split('/')
    elements[-1] = 's%s/%s' % (width, elements[-1])
    return '/'.join(elements)


class Tag(object):
    def __init__(self, entry=None):
        self.set_from_entry(entry)

    def set_from_entry(self, entry=None):
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
            self.params['etag'] = entry.attrib[
                '{http://schemas.google.com/g/2005}etag']
            if entry.find(ATOM + 'id') is not None:
                self.params['id'] = entry.find(
                    ATOM + 'id').text.split('/')[-1]
            else:
                self.params['id'] = None
            if entry.find(
                    ATOM + 'published') is not None:
                self.params['published'] = entry.find(
                    ATOM + 'published').text
            else:
                self.params['published'] = None
            if entry.find(ATOM + 'updated') is not None:
                self.params['updated'] = entry.find(
                    ATOM + 'updated').text
            else:
                self.params['updated'] = None
            if entry.find(ATOM2 + 'edited') is not None:
                self.params['edited'] = entry.find(
                    ATOM2 + 'edited').text
            else:
                self.params['edited'] = None
            if entry.find(ATOM + 'title') is not None:
                self.params['title'] = entry.find(ATOM + 'title').text
            else:
                self.params['title'] = None
            if entry.find(ATOM + 'summary') is not None:
                self.params['summary'] = entry.find(ATOM + 'summary').text
            else:
                self.params['summary'] = None
            for link in entry.findall(ATOM + 'link'):
                self.links[link.attrib['rel']] = {'url': link.attrib['href'],
                                                  'type': link.attrib['type']}

    def get_xml(self):
        return etree.tostring(self.xml, pretty_print=True).decode()

    def __str__(self):
        ans = ''
        for key in self.params.keys():
            ans += '%s -> %s\n' % (key, self.params[key])
        return ans


class Comment(object):
    def __init__(self, entry=None):
        self.set_from_entry(entry)

    def set_from_entry(self, entry=None):
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
            self.params['etag'] = entry.attrib[
                '{http://schemas.google.com/g/2005}etag']
            if entry.find(ATOM + 'id') is not None:
                self.params['id'] = entry.find(ATOM + 'id').text.split('/')[-1]
            else:
                self.params['id'] = None
            if entry.find(ATOM + 'id') is not None:
                self.params['album'] = get_album_id(entry.find(ATOM +
                                                               'id').text)
            else:
                self.params['album'] = None
            if entry.find(ATOM + 'id') is not None:
                self.params['photo'] = get_photo_id(entry.find(ATOM +
                                                               'id').text)
            else:
                self.params['photo'] = None
            if entry.find(ATOM + 'published') is not None:
                self.params['published'] = entry.find(ATOM + 'published').text
            else:
                self.params['published'] = None
            if entry.find(ATOM + 'updated') is not None:
                self.params['updated'] = entry.find(ATOM + 'updated').text
            else:
                self.params['updated'] = None
            if entry.find(ATOM2 + 'edited') is not None:
                self.params['edited'] = entry.find(ATOM2 + 'edited').text
            else:
                self.params['edited'] = None
            if entry.find(ATOM + 'title') is not None:
                self.params['title'] = entry.find(ATOM + 'title').text
            else:
                self.params['title'] = None
            if entry.find(ATOM + 'content') is not None:
                self.params['content'] = entry.find(ATOM + 'content').text
            else:
                self.params['content'] = None
            for link in entry.findall(ATOM + 'link'):
                self.links[link.attrib['rel']] = {'url': link.attrib['href'],
                                                  'type': link.attrib['type']}

    def get_xml(self):
        return etree.tostring(self.xml, pretty_print=True).decode()

    def __str__(self):
        ans = ''
        for key in self.params.keys():
            ans += '%s -> %s\n' % (key, self.params[key])
        return ans


class Photo(object):
    def __init__(self, entry=None):
        self.set_from_entry(entry)

    def set_from_entry(self, entry=None):
        self.params = {}
        self.links = {}
        self.thumbnails = []
        if entry is not None:
            self.xml = entry
            self.params['etag'] = entry.attrib[
                '{http://schemas.google.com/g/2005}etag']
            if entry.find(ATOM + 'id') is not None:
                self.params['id'] = entry.find(
                    ATOM + 'id').text.split('/')[-1]
            else:
                self.params['id'] = None
            if entry.find(ATOM + 'published') is not None:
                self.params['published'] = entry.find(ATOM + 'published').text
            else:
                self.params['published'] = None
            if entry.find(ATOM + 'updated') is not None:
                self.params['updated'] = entry.find(ATOM + 'updated').text
            else:
                self.params['updated'] = None
            if entry.find(ATOM2 + 'edited') is not None:
                self.params['edited'] = entry.find(ATOM2 + 'edited').text
            else:
                self.params['edited'] = None
            if entry.find(ATOM + 'title') is not None:
                self.params['title'] = entry.find(ATOM + 'title').text
            else:
                self.params['title'] = None
            if entry.find(ATOM + 'summary') is not None:
                self.params['summary'] = entry.find(ATOM + 'summary').text
            else:
                self.params['summary'] = None
            if entry.find(ATOM + 'content') is not None:
                self.params['content'] = entry.find(
                    ATOM + 'content').attrib['src']
            else:
                self.params['content'] = None
            if entry.find(PHOTOS + 'albumid') is not None:
                self.params['albumid'] = entry.find(PHOTOS + 'albumid').text
            else:
                self.params['albumid'] = None
            if entry.find(PHOTOS + 'access') is not None:
                self.params['access'] = entry.find(PHOTOS + 'access').text
            else:
                self.params['access'] = None
            if entry.find(PHOTOS + 'width') is not None:
                self.params['width'] = entry.find(PHOTOS + 'width').text
            else:
                self.params['width'] = None
            if entry.find(PHOTOS + 'height') is not None:
                self.params['height'] = entry.find(PHOTOS + 'height').text
            else:
                self.params['height'] = None
            if entry.find(PHOTOS + 'size') is not None:
                self.params['size'] = entry.find(PHOTOS + 'size').text
            else:
                self.params['size'] = None
            if entry.find(PHOTOS + 'timestamp') is not None:
                self.params['timestamp'] = entry.find(
                    PHOTOS + 'timestamp').text
            else:
                self.params['timestamp'] = None
            self.params['url'] = get_total_url(self.params['content'],
                                               self.params['width'])
            self.params['thumbnail2'] = get_total_url(self.params['content'],
                                                      72)
            for link in entry.findall(ATOM + 'link'):
                self.links[link.attrib['rel']] = {'url': link.attrib['href'],
                                                  'type': link.attrib['type']}
            group = entry.find('{http://search.yahoo.com/mrss/}group')
            if group is not None:
                content = group.find('{http://search.yahoo.com/mrss/}content')
                if content is not None:
                    self.params['content'] = content.attrib['url']
                else:
                    self.params['content'] = None
                keywords = group.find(
                    '{http://search.yahoo.com/mrss/}keywords')
                if keywords is not None:
                    self.params['keywords'] = keywords.text
                else:
                    self.params['keywords'] = None
                for th in group.findall(
                        '{http://search.yahoo.com/mrss/}thumbnail'):
                    thumbnail = {'url': th.attrib['url'],
                                 'height': th.attrib['height'],
                                 'width': th.attrib['width']}
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
        return etree.tostring(self.xml, pretty_print=True).decode()

    def __str__(self):
        ans = ''
        for key in self.params.keys():
            ans += '%s -> %s\n' % (key, self.params[key])
        for th in self.thumbnails:
            ans += 'thumbnail (%sx%s): %s\n' % (th['width'], th['height'],
                                                th['url'])
        return ans

    def __lt__(self, other):
        return self.params['published'] > other.params['published']

    def __gt__(self, other):
        return self.params['published'] < other.params['published']


class Album(object):
    def __init__(self, entry=None):
        self.set_from_entry(entry)

    def set_from_entry(self, entry=None):
        self.params = {}
        self.links = {}
        if entry is not None:
            self.xml = entry
            self.params['etag'] = entry.attrib[
                '{http://schemas.google.com/g/2005}etag']
            if entry.find(ATOM + 'id') is not None:
                self.params['id'] = entry.find(ATOM + 'id').text.split('/')[-1]
            else:
                self.params['id'] = None
            if entry.find(ATOM + 'published') is not None:
                self.params['published'] = entry.find(ATOM + 'published').text
            else:
                self.params['published'] = None
            if entry.find(ATOM + 'updated') is not None:
                self.params['updated'] = entry.find(ATOM + 'updated').text
            else:
                self.params['updated'] = None
            if entry.find(ATOM2 + 'edited') is not None:
                self.params['edited'] = entry.find(ATOM2 + 'edited').text
            else:
                self.params['edited'] = None
            if entry.find(ATOM + 'title') is not None:
                self.params['title'] = entry.find(ATOM + 'title').text
            else:
                self.params['title'] = None
            if entry.find(ATOM + 'summary') is not None:
                self.params['summary'] = entry.find(ATOM + 'summary').text
            else:
                self.params['summary'] = None
            if entry.find(ATOM + 'rights') is not None:
                self.params['rights'] = entry.find(ATOM + 'rights').text
            else:
                self.params['rights'] = None
            if entry.find(PHOTOS + 'name') is not None:
                self.params['name'] = entry.find(PHOTOS + 'name').text
            else:
                self.params['name'] = None
            if entry.find(PHOTOS + 'access') is not None:
                self.params['access'] = entry.find(PHOTOS + 'access').text
            else:
                self.params['access'] = None
            if entry.find(PHOTOS + 'timestamp') is not None:
                self.params['timestamp'] = entry.find(
                    PHOTOS + 'timestamp').text
            else:
                self.params['timestamp'] = None
            if entry.find(PHOTOS + 'numphotos') is not None:
                self.params['numphotos'] = entry.find(
                    PHOTOS + 'numphotos').text
            else:
                self.params['numphotos'] = None
            if entry.find(PHOTOS + 'numphotosremaining') is not None:
                self.params['numphotosremaining'] = entry.find(
                    PHOTOS + 'numphotosremaining').text
            else:
                self.params['numphotosremaining'] = None
            if entry.find(PHOTOS + 'bytesUsed') is not None:
                self.params['bytesUsed'] = entry.find(
                    PHOTOS + 'bytesUsed').text
            else:
                self.params['bytesUsed'] = None
            if entry.find(PHOTOS + 'location') is not None:
                self.params['location'] = entry.find(PHOTOS + 'location').text
            else:
                self.params['location'] = None
            if entry.find(PHOTOS + 'user') is not None:
                self.params['user'] = entry.find(PHOTOS + 'user').text
            else:
                self.params['user'] = None
            if entry.find(PHOTOS + 'nickname') is not None:
                self.params['nickname'] = entry.find(PHOTOS + 'nickname').text
            else:
                self.params['nickname'] = None
            for link in entry.findall(ATOM + 'link'):
                self.links[link.attrib['rel']] = {'url': link.attrib['href'],
                                                  'type': link.attrib['type']}
            group = entry.find('{http://search.yahoo.com/mrss/}group')
            if group is not None:
                content = '{http://search.yahoo.com/mrss/}content'
                thumbnail = '{http://search.yahoo.com/mrss/}thumbnail'
                keywords = '{http://search.yahoo.com/mrss/}keywords'
                if group.find(content) is not None:
                    self.params['content'] = group.find(content).attrib['url']
                else:
                    self.params['content'] = None
                if group.find(thumbnail) is not None:
                    self.params['thumbnail'] = group.find(
                        thumbnail).attrib['url']
                    self.params['thumbnail2'] = get_thumbnail_url(
                        self.params['thumbnail'], 100)
                else:
                    self.params['thumbnail'] = None
                    self.params['thumbnail2'] = None
                if group.find(keywords) is not None:
                    self.params['keywords'] = group.find(keywords).text
                else:
                    self.params['keywords'] = None
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
        return etree.tostring(self.xml, pretty_print=True).decode()

    def __str__(self):
        ans = ''
        for key in self.params.keys():
            ans += '%s -> %s\n' % (key, self.params[key])
        return ans

    def __lt__(self, other):
        return self.params['published'] > other.params['published']

    def __gt__(self, other):
        return self.params['published'] < other.params['published']


class Picasa(GoogleService):
    def __init__(self, token_file):
        GoogleService.__init__(
            self,
            auth_url=AUTH_URL,
            token_url=TOKEN_URL,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            token_file=comun.TOKEN_FILE)

    def __do_request(self, method, url, addheaders=None, data=None,
                     params=None, first=True, files=None):
        headers = {'Authorization': 'OAuth %s' % self.access_token,
                   'GData-Version': '2'}
        if addheaders:
            headers.update(addheaders)
        if data:
            if params:
                response = self.session.request(method, url, data=data,
                                                headers=headers,
                                                params=params,
                                                files=files)
            else:
                response = self.session.request(method, url, data=data,
                                                headers=headers, files=files)
        else:
            if params:
                response = self.session.request(method, url, headers=headers,
                                                params=params, files=files)
            else:
                response = self.session.request(method, url, headers=headers,
                                                files=files)
        print(response, response.status_code)
        if response.status_code == 200 or response.status_code == 201:
            return response
        elif (response.status_code == 401 or response.status_code == 403) and\
                first:
            ans = self.do_refresh_authorization()
            if ans:
                return self.__do_request(method, url, addheaders, data,
                                         params, first=False)
        return None

    def get_last_comments(self):
        comments = []
        response = self.__do_request('GET', GET_LAST_COMMENTS_URL)
        if response and response.text:
            answer = response.text.encode()
            root = etree.fromstring(answer)
            entries = root.findall(ATOM + 'entry')
            for entry in entries:
                comments.append(Comment(entry))
        return comments

    def get_tags(self):
        tags = []
        response = self.__do_request('GET', LIST_TAG_URL)
        if response and response.text:
            answer = response.text.encode()
            root = etree.fromstring(answer)
            entries = root.findall(ATOM + 'entry')
            for entry in entries:
                tag = Tag(entry)
                tags.append(tag)
        return tags

    def get_tags_in_photo(self, album_id, photo_id):
        tags = []
        response = self.__do_request('GET', LIST_TAG_IN_PHOTO_URL % (album_id,
                                                                     photo_id))
        if response and response.text:
            answer = response.text.encode()
            root = etree.fromstring(answer)
            entries = root.findall(ATOM + 'entry')
            for entry in entries:
                tag = Tag(entry)
                tags.append(tag)
        return tags

    def get_albums(self):
        albums = []
        params = {'max-results': 100000}
        response = self.__do_request('GET', LIST_ALBUMS_URL, params=params)
        if response and response.text:
            answer = response.text.encode()
            root = etree.fromstring(answer)
            entries = root.findall(ATOM + 'entry')
            for entry in entries:
                album = Album(entry)
                albums.append(album)
        return sorted(albums)

    def get_photo(self, album_id, photo_id):
        photos = self.get_photos(album_id)
        for photo in photos:
            if photo.params['id'] == photo_id:
                return photo
        return None

    def get_album(self, id):
        response = self.__do_request('GET', GET_ALBUM_URL % id)
        if response and response.text:
            return Album(etree.fromstring(response.text.encode()))
        return None

    def add_tag(self, album_id, photo_id, title):
        xml = '<entry xmlns="http://www.w3.org/2005/Atom">\r\n'
        xml += '<title>%s</title>\r\n' % (title)
        xml += '<category scheme="http://schemas.google.com/g/2005#kind" '
        xml += 'term="http://schemas.google.com/photos/2007#tag"/>\r\n'
        xml += '</entry>'
        xml = xml.encode('utf-8')
        response = self.__do_request(
            'POST', ADD_TAG_URL % (album_id, photo_id),
            addheaders={'Content-type': 'application/atom+xml'}, data=xml)
        if response and response.status_code == 201 and response.text:
            return Tag(etree.fromstring(response.text.encode()))
        return None

    def add_album(self, title, summary=None, access=PUBLIC,
                  location=None, keywords=None):
        xml = """<entry xmlns='http://www.w3.org/2005/Atom'
        xmlns:media='http://search.yahoo.com/mrss/'
        xmlns:gphoto='http://schemas.google.com/photos/2007'>
        <title type='text'>%s</title>""" % (title)
        if summary is not None:
            xml += "<summary type='text'>%s</summary>" % (summary)
        if location is not None:
            xml += "<gphoto:location>%s</gphoto:location>" % (location)
        xml += "<gphoto:access>%s</gphoto:access>" % (access)
        xml += "<gphoto:timestamp>%s</gphoto:timestamp>" % (
            int(time.time()*1000))
        if keywords is not None:
            xml += "<media:group><media:keywords>%s\
</media:keywords></media:group>" % (keywords)
        xml += """<category scheme='http://schemas.google.com/g/2005#kind'
        term='http://schemas.google.com/photos/2007#album'></category>
        </entry>"""
        xml = xml.encode('utf-8')
        response = self.__do_request(
            'POST',
            CREATE_ALBUMS_URL,
            addheaders={'Content-type': 'application/atom+xml'}, data=xml)
        if response and response.status_code == 201 and response.text:
            return Album(etree.fromstring(response.text.encode()))
        return None

    def delete_album(self, album):
        return self.__delete_album(album.params['id'])

    def __delete_album(self, id):
        response = self.__do_request(
            'DELETE', DELETE_ALBUM_URL % id, addheaders={'If-match': '*'})
        if response and response.status_code == 200:
            return True
        return False

    def edit_album(self, album):
        id = album.params['id']
        title = album.params['title']
        summary = album.params['summary']
        access = album.params['rights']
        return self.__edit_album(id,
                                 title=title,
                                 summary=summary,
                                 access=access)

    def __edit_album(self, id, title=None, summary=None, location=None,
                     access=PUBLIC, keywords=None):
        album = self.get_album(id)
        if album is not None:
            xml = etree.tostring(album.xml).decode()
            if title is not None:
                xml = xml.replace(
                    '<title>%s</title>' % (album.params['title']),
                    '<title>%s</title>' % (title))
                xml = xml.replace(
                    "<media:title type='plain'>%s</media:title>" % (
                        album.params['title']),
                    "<media:title type='plain'>%s</media:title>" % (title))
            if summary is not None:
                if album.params['summary'] is None:
                    xml = xml.replace(
                        '<summary/>',
                        '<summary>%s</summary>' % (summary))
                else:
                    xml = xml.replace(
                        '<summary>%s</summary>' % (album.params['summary']),
                        '<summary>%s</summary>' % (summary))
            if location is not None:
                if album.params['location'] is None:
                    xml = xml.replace(
                        '<gphoto:location/>',
                        '<gphoto:location>%s</gphoto:location>' % (location))
                else:
                    xml = xml.replace(
                        '<gphoto:location>%s</gphoto:location>' % (
                            album.params['keywords']),
                        '<gphoto:location>%s</gphoto:location>' % (location))
            xml = xml.replace(
                '<rights>%s</rights>' % (album.params['access']),
                '<rights>%s</rights>' % (access))
            xml = xml.replace(
                '<gphoto:access>%s</gphoto:access>' % (
                    album.params['access']),
                '<gphoto:access>%s</gphoto:access>' % (access))
            if keywords is not None:
                if album.params['keywords'] is None:
                    xml = xml.replace(
                        '<media:keywords/>',
                        '<media:keywords>%s</media:keywords>' % (keywords))
                else:
                    xml = xml.replace(
                        '<media:keywords>%s</media:keywords>' % (
                            album.params['keywords']),
                        '<media:keywords>%s</media:keywords>' % (keywords))
            response = self.__do_request(
                'PUT',
                EDIT_ALBUM_URL % id,
                addheaders={'Content-type': 'application/atom+xml',
                            'If-match': '*'},
                data=xml)
            if response and response.status_code == 200 and response.text:
                return Album(etree.fromstring(response.text.encode()))
            else:
                print(response.status.code)
        return None

    def get_photos_in_page(self, album_id, page):
        photos = []
        start_index = (page-1)*10+1
        response = self.__do_request('GET', LIST_PHOTOS_URL2 % (
            album_id, start_index))
        if response and response.text:
            print(response.text)
            answer = response.text.encode()
            root = etree.fromstring(answer)
            entries = root.findall(ATOM + 'entry')
            for entry in entries:
                photo = Photo(entry)
                photos.append(photo)
        return photos

    def get_photos(self, album_id):
        photos = []
        params = {'max-results': 1000}
        response = self.__do_request('GET',
                                     LIST_PHOTOS_URL % album_id,
                                     params=params)
        if response and response.text:
            answer = response.text.encode()
            root = etree.fromstring(answer)
            entries = root.findall(ATOM + 'entry')
            for entry in entries:
                photo = Photo(entry)
                photos.append(photo)
        return sorted(photos)

    def edit_photo_from_id(self,
                           album_id,
                           photo_id,
                           afile,
                           filename=None,
                           caption=None):
        photo = self.get_photo(album_id, photo_id)
        if photo:
            return self.edit_photo(album_id, photo, afile, filename, caption)
        return None

    def edit_photo_from_pixbuf(self, album_id, photo, pixbuf, filename=None,
                               caption=None):
        temp = tempfile.mkstemp(suffix='.png',
                                prefix='picapy_tmp',
                                dir='/tmp')[1]
        if temp is not None and os.path.exists(temp):
            os.remove(temp)
        pixbuf.savev(temp, 'png', (), ())
        ans = self.edit_photo(album_id, photo, temp, filename, caption)
        if temp is not None and os.path.exists(temp):
            os.remove(temp)
            pass
        return ans

    def edit_photo(self, album_id, photo, afile, filename=None, caption=None):
        mime = mimetypes.guess_type(afile)[0]
        content_type = ('Content-Type: %s' % (mime)).encode('utf-8')
        print(afile)
        afilee = open(afile, 'rb')
        data = afilee.read()
        afilee.close()
        xml = etree.tostring(photo.xml).decode()
        if filename is not None:
            xml = xml.replace(
                '<title>%s</title>' % (photo.params['title']),
                '<title>%s</title>' % (filename))
            xml = xml.replace(
                "<media:title type='plain'>%s</media:title>" % (
                    photo.params['title']),
                "<media:title type='plain'>%s</media:title>" % (filename))
        if caption is not None:
            if photo.params['summary'] is None:
                xml = xml.replace(
                    '<summary/>',
                    '<summary>%s</summary>' % (caption))
            else:
                xml = xml.replace(
                    '<summary>%s</summary>' % (photo.params['summary']),
                    '<summary>%s</summary>' % (caption))
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
        url = EDIT_PHOTO_URL % (album_id, photo.params['id'])
        response = self.__do_request(
            'PUT',
            url,
            addheaders={
                'Content-type': 'multipart/related; boundary="END_OF_PART"',
                'Content-length': str(len(body)), 'MIME-version': '1.0',
                'If-Match': '*'},
            data=body)
        if response and response.status_code == 200 and response.text:
            return Photo(etree.fromstring(response.text.encode()))
        return None

    def add_image_from_pixbuf(self,
                              album_id,
                              pixbuf,
                              title,
                              comment,
                              reduce_size,
                              size,
                              colors):
        temp = tempfile.mkstemp(suffix='.png',
                                prefix='picapy_tmp',
                                dir='/tmp')[1]
        pixbuf.savev(temp, 'png', (), ())
        photo = self.add_image(album_id,
                               temp,
                               title,
                               comment,
                               reduce_size,
                               size,
                               colors)
        if temp is not None and os.path.exists(temp):
            os.remove(temp)
        return photo

    def add_image(self,
                  album_id,
                  imagename,
                  title,
                  comment,
                  reduce_size=False,
                  size=800,
                  colors=False):
        mime = mimetypes.guess_type(imagename)[0]
        if mime in SUPPORTED_MIMES or mime in CONVERTED_MIMES:
            temp = None
            if reduce_size is True or colors is True or\
                    mime in CONVERTED_MIMES:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(imagename)
                temp = tempfile.mkstemp(suffix='.png', prefix='picapy_tmp',
                                        dir='/tmp')[1]
                if reduce_size is True:
                    pixbuf = picasamod.scale_pixbuf(pixbuf, size)
                    print('reduced size of %s' % temp)
                if colors is True:
                    pixbuf = picasamod.grayscale_pixbuf(pixbuf)
                    print(('reduced colors of %s' % temp))
                pixbuf.savev(temp, 'png', [], [])
                print(('%s converted!' % temp))
                imagename = temp
            ans = self.add_photo(album_id,
                                 afile=imagename,
                                 filename=title,
                                 caption=comment)
            print('The ans %s' % ans)
            if temp is not None and os.path.exists(temp):
                os.remove(temp)
            if ans:
                return ans
        return None

    def add_photo(self,
                  album_id,
                  afile,
                  filename=None,
                  caption=None):
        if filename is None:
            filename = afile.split('/')[-1]
        filename = ('<title>%s</title>\r\n' % (filename))
        if caption is None:
            caption = afile.split('/')[-1].split('.')[0]
        caption = ('<summary>%s</summary>\r\n' % (caption))
        body_text = io.StringIO()
        body_text.write('Media multipart posting\r\n')
        body_text.write('--END_OF_PART\r\n')
        body_text.write('Content-Type: application/atom+xml\r\n\r\n')
        body_text.write('<entry xmlns="http://www.w3.org/2005/Atom">\r\n')
        body_text.write(filename)
        body_text.write(caption)
        body_text.write(
            '<category scheme="http://schemas.google.com/g/2005#kind" ')
        body_text.write(
            'term="http://schemas.google.com/photos/2007#photo"/>\r\n')
        body_text.write('</entry>\r\n\r\n')
        body_text.write('--END_OF_PART\r\n')
        body_text.write(
            'Content-Type: %s\r\n' % (mimetypes.guess_type(afile)[0]))
        body_text.write('MIME-Version: 1.0\r\n\r\n')
        body = io.BytesIO()
        body.write(body_text.getvalue().encode('utf-8'))
        afilee = open(afile, 'rb')
        data = afilee.read()
        afilee.close()
        body.write(data)
        body.write('\r\n--END_OF_PART--'.encode('utf-8'))
        body = body.getvalue()
        response = self.__do_request(
            'POST',
            INSERT_PHOTO_URL % album_id,
            addheaders={
                'Content-type': 'multipart/related; boundary="END_OF_PART"',
                'Content-length': str(len(body)),
                'MIME-version': '1.0'},
            data=body)
        if response and response.status_code == 201 and response.text:
            return Photo(etree.fromstring(response.text.encode()))
        return None

    def delete_tag_in_photo(self, album_id, photo_id, tag_id):
        response = self.__do_request(
            'DELETE',
            DELETE_TAG_IN_PHOTO_URL % (album_id,
                                       photo_id,
                                       tag_id))
        if response and (response.status_code == 200 or
                         response.status_code == 404):
            return True
        return False

    def delete_photo(self, album, photo):
        return self.__delete_photo(album.params['id'], photo.params['id'])

    def __delete_photo(self, album_id, photo_id):
        response = self.__do_request(
            'DELETE',
            DELETE_PHOTO_URL % (album_id, photo_id),
            addheaders={'If-match': '*'})
        if response and response.status_code == 200:
            return True
        return False


if __name__ == '__main__':
    pi = Picasa(token_file=comun.TOKEN_FILE)
    print(pi.do_refresh_authorization())
    print(pi.get_albums()[0])
    # pi.do_revoke_authorization()
    ans = pi.add_photo(
        '5803966623150991473',
        "/home/atareao/Imágenes/G'MIC para GIMP 64 bits - 1.5.6.1_031.png")
    print(ans)
    print(pi.get_album('5426716353448836273'))
    # print(pi.get_photos_in_page('5803966623150991473', 1))
    ans = pi.edit_photo_from_id(
        '5811515891101718113',
        '5811517614627182034',
        '/home/atareao/Imágenes/0028_Tribler 6.0.0.png')
    if ans:
        print(ans)
    exit(0)

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

import os
import locale
import gettext

######################################


def is_package():
    return __file__.find('src') < 0

######################################


APPNAME = 'Picapy'
APP = 'picapy'
APP_CONF = APP+'.conf'
ICON = 'picapy'
CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config')
CONFIG_APP_DIR = os.path.join(CONFIG_DIR, APP)
IMAGES_DIR = os.path.join(CONFIG_APP_DIR, 'images')
CONFIG_FILE = os.path.join(CONFIG_APP_DIR, APP_CONF)
TOKEN_FILE = os.path.join(CONFIG_APP_DIR, 'token')

if not os.path.exists(CONFIG_APP_DIR):
    os.makedirs(CONFIG_APP_DIR)
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

# check if running from source
if is_package():
    ROOTDIR = '/opt/extras.ubuntu.com/picapy/share/'
    LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
    APPDIR = os.path.join(ROOTDIR, APP)
    CHANGELOG = os.path.join(APPDIR, 'changelog')
    IMGDIR = APPDIR
else:
    ROOTDIR = os.path.dirname(__file__)
    LANGDIR = os.path.normpath(os.path.join(ROOTDIR, '../po'))
    APPDIR = ROOTDIR
    DEBIANDIR = os.path.normpath(os.path.join(ROOTDIR, '../debian'))
    CHANGELOG = os.path.join(DEBIANDIR, 'changelog')
    IMGDIR = os.path.normpath(os.path.join(ROOTDIR, '../data/icons'))

f = open(CHANGELOG, 'r')
line = f.readline()
f.close()
pos = line.find('(')
posf = line.find(')', pos)
VERSION = line[pos+1:posf].strip()
if not is_package():
    VERSION = VERSION + '-src'


ICON = os.path.join(IMGDIR, 'picapy.svg')
DEFAULT_ALBUM = os.path.join(IMGDIR, 'default_album.svg')
DEFAULT_PHOTO = os.path.join(IMGDIR, 'default_photo.svg')


try:
    current_locale, encoding = locale.getdefaultlocale()
    language = gettext.translation(APP, LANGDIR, [current_locale])
    language.install()
    if sys.version_info[0] == 3:
        _ = language.gettext
    else:
        _ = language.ugettext
except Exception as e:
    print(e)
    _ = str

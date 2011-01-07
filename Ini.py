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
import ConfigParser
import os
from Crypto.Cipher import AES
import base64
import os

# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32

# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '&'

MK = 'YlF1YfNqaLpgRQ21rlyOpM1RpHztgKhi9t7YAB9+3i8=CDYU/qPgmqo4bzeqqvG86GeXgZYrPFc0RgkjEx2NCaE=GAfPmvXMxZrh1sBwnM4QbRF65EcOirhjU0lAFJWhe+I=4SnMYszjwos5XUCTxDp7a5pe4fcxt/EWP/iQ96h1WNA=/g689L9NBj0wNdSSu48jEL5bGpsoDv6JlIxi0cJ3LGI='

class Encoder:
	def __init__(self):
		AE=MK[30:80]
		self.cipher = AES.new(self.pad(AE[10:41]))
	
	def encode(self,cadena):
		return base64.b64encode(self.cipher.encrypt(self.pad(cadena)))
	
	def decode(self,cadena):
		return self.cipher.decrypt(base64.b64decode(cadena)).rstrip(PADDING)
	
	def pad(self,cadena):
		return cadena + (BLOCK_SIZE - len(cadena) % BLOCK_SIZE) * PADDING

VERSION = '2.0'

class Ini:
	def __init__(self,inifile):
		self.inifile=inifile
		self.email=''
		self.password=''
		self.encoder = Encoder()
		if os.path.exists(inifile)==False:
			self.write()

	def read(self):
		ini=ConfigParser.ConfigParser()
		ini.read(self.inifile)
		if ini.has_section('Defecto'):
			os.remove(self.inifile)
			self.write()
		if not ini.has_section('Configuration'):
			self.write()
		else:
			self.email=self.encoder.decode(ini.get('Configuration','Email'))
			self.password=self.encoder.decode(ini.get('Configuration','Password'))
			self.version=self.encoder.decode(ini.get('Configuration','Version'))

	def write(self):
		ini=ConfigParser.ConfigParser()
		ini.read(self.inifile)
		if not ini.has_section('Configuration'):
			ini.add_section('Configuration')
		ini.set('Configuration','Password',self.encoder.encode(self.password))
		ini.set('Configuration','Email',self.encoder.encode(self.email))
		ini.set('Configuration','Version',self.encoder.encode(VERSION))
		with open(self.inifile,'wb') as writefile:
			ini.write(writefile)
	def get_email(self):
		return self.email
	def get_password(self):
		return self.password
	def set_email(self,email):
		self.email=email
	def set_password(self,password):
		self.password=password

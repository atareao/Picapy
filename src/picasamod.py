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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

COUNTERCLOCKWISE = GdkPixbuf.PixbufRotation.COUNTERCLOCKWISE
UPSIDEDOWN = GdkPixbuf.PixbufRotation.UPSIDEDOWN
CLOCKWISE = GdkPixbuf.PixbufRotation.CLOCKWISE

def scale_pixbuf(pixbuf,size):
    w = pixbuf.get_width()
    h = pixbuf.get_height()
    if w>size or h>size:
        if w > h:
            h = int(h * size/w)
            w = int(size)
        else:
            w = int(w * size/h)
            h = int(size)
        pixbuf = GdkPixbuf.Pixbuf.scale_simple(pixbuf,w,h, GdkPixbuf.InterpType.HYPER)
    return pixbuf

def rotate_pixbuf(pixbuf,rotation):
    return GdkPixbuf.Pixbuf.rotate_simple(pixbuf,rotation)

def flip_pixbuf(pixbuf,horizontal):
    return GdkPixbuf.Pixbuf.flip(pixbuf,horizontal)

def grayscale_pixbuf(pixbuf):
    grayscale = pixbuf.copy()
    pixbuf.saturate_and_pixelate(grayscale, 0.0, False)
    return grayscale
def get_array_of_colors(pixbuf):
    colors = []
    alist = pixbuf.get_pixels()
    if pixbuf.get_has_alpha():
        rows = 4
    else:
        rows = 3
    for cont in range(0,len(alist),rows):
        color=tuple(alist[cont:cont+rows])
        #col=Gdk.RGBA(float(color[0])/256.,float(color[1])/256.,float(color[2])/256.,float(color[3])/256.)
        colors.append(color)
        #print(col)
    return colors
def int2byte(aint):
    return bytes((aint,))
def get_string_from_array_of_colors(colors,alpha=False):
    data = b''
    if alpha:
        for color in colors:
            data+=int2byte(color[0])+int2byte(color[1])+int2byte(color[2])
    else:
        for color in colors:
            data+=int2byte(color[0])+int2byte(color[1])+int2byte(color[2])+int2byte(color[3])
    return data
def reduce_colors_pixbuf(pixbuf):
    colors = get_array_of_colors(pixbuf)
    alpha = pixbuf.get_has_alpha()
    print(pixbuf.get_bits_per_sample())
    print(pixbuf.get_rowstride())
    existing = []
    data = {}
    percentage = int(0.0001* len(colors))
    if percentage <= 0:
        percentage = 1
    print(percentage)
    for i in range(0,len(colors),percentage):
        color = colors[i]
        if color in existing:
            data[color] +=1
        else:
            existing.append(color)
            data[color] = 1
    print(data)
    print(get_string_from_array_of_colors(colors,alpha))

    #color=tuple(map(ord, pixbuf.get_pixels()[:3]))
    #col=Gdk.RGBA(float(color[0])/256.,float(color[1])/256.,float(color[2])/256.)
    #self.cp.set_current_rgba(col)

if __name__ == '__main__':
    entrada = '/home/atareao/Imágenes/0029_Tribler 6.0.0.png'
    salida = '/home/atareao/Imágenes/test.png'
    #
    pixbufinput =  GdkPixbuf.Pixbuf.new_from_file(entrada)
    pixbufoutput = grayscale_pixbuf(pixbufinput)
    pixbufoutput = rotate_pixbuf(pixbufoutput,CLOCKWISE)
    pixbufoutput = flip_pixbuf(pixbufoutput,True)
    #pixbufoutput = reduce_colors_pixbuf(pixbufinput)
    #print(GdkPixbuf.Pixbuf.save_to_stream(pixbufoutput,filestream,'png',None,None))
    pixbufoutput.savev(salida,'png',[],[])
    print('end')
    #pixbufoutput.savev(salida,'png',(),())
    exit(0)

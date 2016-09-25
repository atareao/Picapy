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

from PIL import Image
import random
import sys


class CImageInstagram:
    def __init__(self, filename=None):
        self.name = filename
        self.im = Image.open(filename)

    def setDecription(self, description=None):
        self.desc = description

    def printDescription(self):
        print(self.desc)

    def setFilter(self, filter=None):
        self.im = self.im.filter(filter)
        self.im = self.im.show()

    def applyFilter(self, aCFilter):
        self.im_copy = aCFilter.applyFilter(self.im)

    def saveImg(self, dst):
        self.im_copy.save(dst)

    def saveThumb(self, dst, w, h):
        thumb = self.im_copy.thumbnail((w, h), Image.ANTIALIAS)
        self.im_copy.save(dst)


class CFilter:
    def applyFilter(self, aImage):
        pass
# our filters


class CFilterSunset(CFilter):
    # makes the image look nice
    def applyFilter(self, aImage):
        if aImage.mode == 'RGB':
            new_image = Image.new('RGB', aImage.size)
            new_image_list = []

            max_width = aImage.size[0]
            max_height = aImage.size[1]
            all_pixels = aImage.getdata()
            x = 0
            y = 0

            for i in range(len(all_pixels)):
                factor = 1.25 - float(y)/float(max_height)
                if i > 0 and i == max_width*(y + 1):
                    x = 0
                    y += 1
                x += 1
                # get the pixel
                pixel = all_pixels[i]
                # create a new pixel with some factors on each color
                new_pixel = (int(pixel[0]*1.2*factor),
                             int(pixel[1]*0.7*factor),
                             int(pixel[2]*0.5*factor))
                # append the new pixel to the new_image_list
                new_image_list.append(new_pixel)
            # make a new image
            new_image.putdata(new_image_list)
            return new_image
        return aImage


class CFilterColorful(CFilter):
    def applyFilter(self, aImage):
        def sqrt(a):
            return a**0.5

        if aImage.mode == 'RGB':
            # create a new image
            new_image = Image.new('RGB', aImage.size)
            new_pixel_list = []
            # get some dimensions
            max_width = aImage.size[0]
            max_height = aImage.size[1]
            center_x = max_width/2
            center_y = max_height/2
            max_distance = sqrt(center_x**2 + center_y**2)
            x = 0
            y = 0
            # get all the pixels
            pixels = aImage.getdata()
            # iterate through all pixels
            for i in range(len(pixels)):
                # reset x and go to next row when we're at the edge
                # of the image
                if i > 0 and i == (max_width*(y+1)):
                    x = 0
                    y += 1
                # factor is a percentage of the max distance
                f = 1.00 - sqrt((center_x - x)**2 +
                                (center_y - y)**2)/max_distance
                r = pixels[i][0]
                g = pixels[i][1]
                b = pixels[i][2]
                # add one to x
                x += 1
                # get some factors
                if 0.66 < f < 1.0:
                    r = int(r*(1.00-f))
                elif 0.33 < f < 0.66:
                    g = int(g*(1.00-f))
                elif 0.0 < f < 0.33:
                    b = int(b*(1.00-f))

                # add a new pixel to the new pixel-list
                new_pixel_list.append((r, g, b))

            new_image.putdata(new_pixel_list)
            return new_image
        return aImage


class CFilterGroovy(CFilter):

    def applyFilter(self, aImage):
        def sqrt(a):
            return a**0.5

        if aImage.mode == 'RGB':
            # create a new image
            new_image = Image.new('RGB', aImage.size)
            new_pixel_list = []

            # get some dimensions
            max_width = aImage.size[0]
            max_height = aImage.size[1]
            center_x = max_width/2
            center_y = max_height/2
            max_distance = sqrt(center_x**2 + center_y**2)
            x = 0
            y = 0

            # get all the pixels
            pixels = aImage.getdata()

            # iterate through all pixels
            for i in range(len(pixels)):
                # reset x and go to next row when we're at the edge
                # of the image
                red_factor = 0.5
                if i > 0 and i == max_width*(y+1):
                    x = 0
                    y += 1
                # factor is a percentage of the max distance
                factor = 1.1 - sqrt((center_x - x)**2 +
                                    (center_y - y)**2)/max_distance
                # red_factor is weird
                red_factor = 0.1 + factor/red_factor
                # add one to x
                x += 1
                # add a new pixel to the new pixel-list
                new_pixel_list.append((int(pixels[i][0]*red_factor*factor),
                                       int(pixels[i][1]*factor),
                                       int(pixels[i][2]*factor)))
            new_image.putdata(new_pixel_list)
            return new_image
        return aImage


class CFilterVignette(CFilter):
    # finally
    def applyFilter(self, aImage):
        def sqrt(a):
            return a**0.5
        if aImage.mode == 'RGB':
            # create a new image
            new_image = Image.new('RGB', aImage.size)
            new_pixel_list = []
            # get some dimensions
            max_width = aImage.size[0]
            max_height = aImage.size[1]
            center_x = max_width/2
            center_y = max_height/2
            max_distance = sqrt(center_x**2 + center_y**2)
            x = 0
            y = 0
            # get all the pixels
            pixels = aImage.getdata()
            # iterate through all pixels
            for i in range(len(pixels)):
                # reset x and go to next row when we're at the
                # edge of the image
                if i > 0 and i == max_width*(y+1):
                    x = 0
                    y += 1
                # factor is a percentage of the max distance
                factor = 1.00 - sqrt((center_x - x)**2 +
                                     (center_y - y)**2)/max_distance
                # add one to x
                x += 1
                # add a new pixel to the new pixel-list
                new_pixel_list.append((int(pixels[i][0]*factor),
                                      int(pixels[i][1]*factor),
                                      int(pixels[i][2]*factor)))
            new_image.putdata(new_pixel_list)
            return new_image
        return aImage


class CFilterFade(CFilter):
    def applyFilter(self, aImage):
        if aImage.mode == 'RGB':
            new_image = Image.new('RGB', aImage.size)
            new_image_list = []
            max_width = aImage.size[0]
            all_pixels = aImage.getdata()
            x = 0
            y = 0
            for i in range(len(all_pixels)):
                if i > 0 and i == max_width*(y+1):
                    x = 0
                    y += 1
                factor = 1.2 - float(x)/float(max_width)
                x += 1
                # get the pixel
                pixel = all_pixels[i]
                # create a new pixel with some factors on each color
                new_pixel = (int(pixel[0]*factor),
                             int(pixel[1]*0.9*factor),
                             int(pixel[2]*0.8*factor))
                # append the new pixel to the new_image_list
                new_image_list.append(new_pixel)
            # make a new image
            new_image.putdata(new_image_list)
        return new_image


class CFilterBlue(CFilter):
    def applyFilter(self, aImage):
        if aImage.mode == 'RGB':
            new_image = Image.new('RGB', aImage.size)
            new_image_list = []
            all_pixels = aImage.getdata()
            for i in range(len(all_pixels)):
                pixel = all_pixels[i]
                new_image_list.append((int(pixel[0]),
                                       int(pixel[1]),
                                       int(pixel[2]*1.5)))
            new_image.putdata(new_image_list)
            return new_image


class CFilterGreen(CFilter):
    def applyFilter(self, aImage):
        if aImage.mode == 'RGB':
            new_image = Image.new('RGB', aImage.size)
            new_image_list = []
            all_pixels = aImage.getdata()
            for i in range(len(all_pixels)):
                pixel = all_pixels[i]
                new_image_list.append((int(pixel[0]),
                                       int(pixel[1]*1.25),
                                       int(pixel[2])))
            new_image.putdata(new_image_list)
            return new_image


class CFilterRed(CFilter):
    def applyFilter(self, aImage):
        if aImage.mode == 'RGB':
            new_image = Image.new('RGB', aImage.size)
            new_image_list = []
            all_pixels = aImage.getdata()
            for i in range(len(all_pixels)):
                pixel = all_pixels[i]
                new_image_list.append((int(pixel[0]*1.25),
                                       int(pixel[1]),
                                       int(pixel[2])))
            new_image.putdata(new_image_list)
            return new_image


class CFilterBrighten(CFilter):
    def applyFilter(self, aImage):
        new_image = Image.new('RGB', aImage.size)
        new_image_list = []
        pixels = aImage.getdata()
        # Perform algorithmic calculations here
        for i in range(0, len(pixels)-1):
            r = pixels[i][0]
            g = pixels[i][1]
            b = pixels[i][2]
            r = int(r + (pixels[i+1][0]/4))
            g = int(g + (pixels[i+1][1]/4))
            b = int(b + (pixels[i+1][2]/4))
            new_image_list.append((r, g, b))
        # append the pixels to the new array
        new_image.putdata(new_image_list)
        return new_image


class CFilterOld(CFilter):
    def applyFilter(self, aImage):
        new_image = Image.new('RGB', aImage.size)
        new_image_list = []
        pixels = aImage.getdata()
        for i in range(0, len(pixels)-1):
            r = pixels[i][0]
            g = pixels[i][1]
            b = pixels[i][2]
            if random.randint(1, 100) > 20:
                g = int(r*0.9)
                b = g
            new_image_list.append((r, g, b))
        # append the pixels to the new array
        new_image.putdata(new_image_list)
        return new_image


class Filters:

    def __init__(self):
        self.filt_list = {'Sunset': CFilterSunset(),
                          'Colorful': CFilterColorful(),
                          'Groovy': CFilterGroovy(),
                          'Vignette': CFilterVignette(),
                          'Fade': CFilterFade(),
                          'Blue': CFilterBlue(),
                          'Green': CFilterGreen(),
                          'Red': CFilterRed(),
                          'Brighten': CFilterBrighten(),
                          'Old': CFilterOld()}
        self.keyList = []
        for key in self.filt_list.keys():
            self.keyList.append(key)

    def getFilter(self, str):
        # Don't want the whole server to crash if someone tries to post-data
        # something inaccurate, catch the error if it wasn't found.
        try:
            return self.filt_list[str]
        except:
            return None

    def getKeys(self):
        return self.keyList

if __name__ == '__main__':
    import os
    thedir = os.path.join(os.path.normpath(os.path.join(__file__, '..', '..')),
                          'sample')
    afile = Image.open(os.path.join(thedir, 'sample.jpg'))
    filters = Filters()
    for afilter in filters.keyList:
        print(afilter)
        newfile = filters.getFilter(afilter).applyFilter(afile)
        newfile.save(os.path.join(thedir, afilter+'.jpg'))

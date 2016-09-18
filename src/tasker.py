#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is part of picapy
#
# Copyright (C) 2015-2016 Lorenzo Carbonell
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
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(1)
from idleobject import IdleObject
from threading import Thread
from gi.repository import GObject


class Tasker(IdleObject, Thread):
    __gsignals__ = {
        'start-one-element': (GObject.SIGNAL_RUN_FIRST,
                              GObject.TYPE_NONE,
                              (object,)),
        'end-one-element': (GObject.SIGNAL_RUN_FIRST,
                            GObject.TYPE_NONE,
                            (object,)),
        'finished': (GObject.SIGNAL_RUN_FIRST,
                     GObject.TYPE_NONE,
                     ()),
        'stopped': (GObject.SIGNAL_RUN_FIRST,
                    GObject.TYPE_NONE,
                    ())
        }

    def __init__(self, task_to_do, elements, *args):
        IdleObject.__init__(self)
        Thread.__init__(self)
        self.task_to_do = task_to_do
        self.elements = elements
        self.args = args
        self.stop = False
        self.daemon = True

    def stopit(self, *args):
        self.stop = True

    def run(self):
        for anelement in self.elements:
            if self.stop:
                self.emit('stopped')
                break
            self.emit('start-one-element', anelement)
            answer = self.task_to_do(anelement, *self.args)
            self.emit('end-one-element', answer)
        self.emit('finished')

if __name__ == '__main__':
    import time

    def contador(hasta, nombre1, nombre2):
        writer = open('/home/lorenzo/prueba.txt', 'w')
        for i in range(0, hasta):
            writer.write('%s %s %s %s\n' % (time.time(), i, nombre1, nombre2))
        writer.close()
    print(1)
    contador(4, 'n1', 'n2')
    elements = [4, 7, 8]
    tasker = Tasker(contador, elements, 'n1', 'n2')
    tasker.start()
    print(2)
    time.sleep(3)

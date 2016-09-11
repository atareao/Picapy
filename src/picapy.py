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
    gi.require_version('Gio', '2.0')
    gi.require_version('GLib', '2.0')
    gi.require_version('GdkPixbuf', '2.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GdkPixbuf
import sys
import os
import webbrowser
from mainwindow import MainWindow
import comun
from comun import _


class MainApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(
            self,
            application_id='es.atareao.picapy',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.license_type = Gtk.License.GPL_3_0

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)

    def on_quit(self, widget, data):
        self.quit()

    def do_startup(self):
        Gtk.Application.do_startup(self)

        def create_action(name,
                          callback=self.action_clicked,
                          var_type=None,
                          value=None):
            if var_type is None:
                action = Gio.SimpleAction.new(name, None)
            else:
                action = Gio.SimpleAction.new_stateful(
                    name,
                    GLib.VariantType.new(var_type),
                    GLib.Variant(var_type, value)
                )
            action.connect('activate', callback)
            return action

        self.add_action(create_action('quit', callback=lambda *_: self.quit()))
        self.set_accels_for_action('app.quit', ['<Ctrl>Q'])

        self.add_action(create_action('up',
                                      callback=self.on_up_action))
        self.add_action(create_action('add',
                                      callback=self.on_add_action))
        self.add_action(create_action('remove',
                                      callback=self.on_remove_action))
        self.add_action(create_action('download',
                                      callback=self.on_download_action))
        self.add_action(create_action('slideshow',
                                      callback=self.on_slideshow_action))
        self.add_action(create_action(
            'set_preferences',
            callback=self.on_preferences_activate))
        self.add_action(create_action(
            'goto_homepage',
            callback=lambda x, y: webbrowser.open(
                'http://www.atareao.es/apps/\
crear-un-gif-animado-de-un-video-en-ubuntu-en-un-solo-clic/')))
        self.add_action(create_action(
            'goto_bug',
            callback=lambda x, y: webbrowser.open(
                    'https://bugs.launchpad.net/2gif')))
        self.add_action(create_action(
            'goto_sugestion',
            callback=lambda x, y: webbrowser.open(
                    'https://blueprints.launchpad.net/2gif')))
        self.add_action(create_action(
            'goto_translation',
            callback=lambda x, y: webbrowser.open(
                    'https://translations.launchpad.net/2gif')))
        self.add_action(create_action(
            'goto_questions',
            callback=lambda x, y: webbrowser.open(
                    'https://answers.launchpad.net/2gif')))
        self.add_action(create_action(
            'goto_twitter',
            callback=lambda x, y: webbrowser.open(
                    'https://twitter.com/atareao')))
        self.add_action(create_action(
            'goto_google_plus',
            callback=lambda x, y: webbrowser.open(
                    'https://plus.google.com/\
118214486317320563625/posts')))
        self.add_action(create_action(
            'goto_facebook',
            callback=lambda x, y: webbrowser.open(
                    'http://www.facebook.com/elatareao')))
        self.add_action(create_action(
            'goto_donate',
            callback=self.on_support_clicked))
        self.add_action(create_action(
            'about',
            callback=self.on_about_activate))

    def do_activate(self):
        print('activate')
        self.win = MainWindow(self)
        self.add_window(self.win)
        self.win.show()

    def action_clicked(self, action, variant):
        print(action, variant)
        if variant:
            action.set_state(variant)

    def on_support_clicked(self, widget, optional):
        pass

    def on_preferences_activate(self, widget, optional):
        self.win.on_preferences_activate(widget)

    def on_open_file_clicked(self, widget, optional):
        pass

    def on_up_action(self, widget, optional):
        self.win.on_button1_clicked()

    def on_add_action(self, widget, optional):
        self.win.on_button2_clicked()

    def on_remove_action(self, widget, optional):
        self.win.on_remove_button_clicked()

    def on_download_action(self, widget, optional):
        self.win.on_descargar_activated()

    def on_slideshow_action(self, widget, optional):
        self.win.on_preview_activated()

    def on_about_activate(self, widget, optional):
        """Create and populate the about dialog."""
        about_dialog = Gtk.AboutDialog(parent=self.win)
        about_dialog.set_name(comun.APPNAME)
        about_dialog.set_version(comun.VERSION)
        about_dialog.set_copyright(
            'Copyrignt (c) 2015-2016\nLorenzo Carbonell Cerezo')
        about_dialog.set_comments(_('An app to convert video to gif'))
        about_dialog.set_license('''
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
''')
        ad.set_website('https://www.atareao.es')
        ad.set_website_label('https://www.atareao.es')
        ad.set_authors([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_documenters([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_translator_credits('''
'Dario Villar Veres <dario.villar.v@gmail.com>\n'+
'Bernardo Miguel	Savone <bmsavone@gmail.com>\n'+
'Enbata <peionz@euskalnet.net>\n'+
'Mario Blättermann <mariobl@gnome.org>\n'+
'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>\n'+
'zeugma <https://launchpad.net/~sunder67>\n'+
'Alin Andrei <https://launchpad.net/~nilarimogard>\n'+
'Fitoschido <fitoschido@gmail.com>\n'+
'Daniele Lucarelli <https://launchpad.net/~ldanivvero>\n'+
'Alejandro Martín Covarrubias <alex.covarrubias@gmail.com>\n'+
'Rustam Vafin\n'+
'elmodos\n'+
'extraymond@gmail.com <extraymond@gmail.com>\n'+
'fgp <https://launchpad.net/~komakino>\n''')
        about_dialog.set_icon(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        about_dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        about_dialog.set_program_name(comun.APPNAME)
        about_dialog.run()
        about_dialog.destroy()


def main():
    app = MainApplication()
    app.run(None)

if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Created by Izidor "iyonius" Matušov <izidor.matusov@gmail.com>
#            on 04.11.2011

import gtk
import pygtk

class SettingsWindow(gtk.Window):
    def __init__(self):
        super(SettingsWindow, self).__init__()

        self.set_border_width(10)

        main_vbox = gtk.VBox(False, 15)

        alignment = gtk.Alignment(0, 0, 0, 0)
        label = gtk.Label()
        label.set_use_markup(True)
        label.set_markup('<b><span size="16000">Yet Another Timer</span></b>')
        alignment.add(label)
        main_vbox.pack_start(alignment, False, False, 3)

        frame = gtk.Frame('Notify me:')
        vbox = gtk.VBox(False, 7)
        vbox.set_border_width(10)
        frame.add(vbox)

        hbox = gtk.HBox(False, 5)
        self.in_box = gtk.RadioButton(label='in')
        hbox.pack_start(self.in_box, False, False, 5)
        adjustment = gtk.Adjustment(0, 0, 999, 1, 10)
        self.in_hours = gtk.SpinButton(adjustment)
        # Alignment to right
        self.in_hours.set_alignment(1.0)
        self.in_hours.set_width_chars(3)
        hbox.pack_start(self.in_hours, False)
        hbox.pack_start(gtk.Label('hours'), False)
        adjustment = gtk.Adjustment(0, 0, 999, 1, 10)
        self.in_minutes = gtk.SpinButton(adjustment)
        self.in_minutes.set_alignment(1.0)
        self.in_minutes.set_width_chars(3)
        hbox.pack_start(self.in_minutes, False)
        hbox.pack_start(gtk.Label('minutes'), False)
        vbox.pack_start(hbox, False)

        hbox = gtk.HBox(False, 2)
        self.at_box = gtk.RadioButton(self.in_box, 'at')
        hbox.pack_start(self.at_box, False, False, 5)
        adjustment = gtk.Adjustment(0, 0, 23, 1, 10)
        self.at_hours = gtk.SpinButton(adjustment)
        self.at_hours.set_wrap(True)
        # Alignment to right
        self.at_hours.set_alignment(1.0)
        self.at_hours.set_width_chars(2)
        hbox.pack_start(self.at_hours, False)
        hbox.pack_start(gtk.Label(':'), False)
        adjustment = gtk.Adjustment(0, 0, 59, 1, 10)
        self.at_minutes = gtk.SpinButton(adjustment)
        self.at_minutes.set_wrap(True)
        # Alignment to right
        self.at_minutes.set_alignment(1.0)
        self.at_minutes.set_width_chars(2)
        hbox.pack_start(self.at_minutes, False)

        vbox.pack_start(hbox, False)

        main_vbox.pack_start(frame, False)

        hbox = gtk.HBox(False, 5)
        hbox.pack_start(gtk.Label('Message:'), False)
        self.message = gtk.Entry()
        hbox.pack_start(self.message)

        main_vbox.pack_start(hbox, False)

        alignment = gtk.Alignment(1, 0, 0, 0)
        button = gtk.Button(stock=gtk.STOCK_EXECUTE)
        alignment.add(button)
        main_vbox.pack_start(alignment, False)


        self.add(main_vbox)

sw = SettingsWindow()
sw.show_all()

sw.connect('destroy', gtk.main_quit)
gtk.main()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

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
    """ Allows the user to enter parameters of notification. """

    def __init__(self):
        """ Builds GUI and set default values """
        super(SettingsWindow, self).__init__()

        self.set_border_width(10)
        self.set_title('Yet Another Timer')
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)

        gui = self._build_gui()
        self.add(gui)

        # Set default parameters
        self.in_box.set_active(True)
        self.on_in_at_changed(self.in_box, 'in')
        self.set_message('The time is up!')

        # Caching results after destroying window
        self.connect('destroy', self.on_destroy)
        self.result_time = None
        self.result_message = None

    def _build_gui(self):
        """ Creates GUI and return the main element """

        main_vbox = gtk.VBox(False, 15)

        # A heading
        alignment = gtk.Alignment(0, 0, 0, 0)
        label = gtk.Label()
        label.set_use_markup(True)
        # size must be (size in pt)*1000
        label.set_markup('<b><span size="16000">Yet Another Timer</span></b>')
        alignment.add(label)
        main_vbox.pack_start(alignment, False, False, 3)

        # Framebox for times
        frame = gtk.Frame('Notify me:')
        vbox = gtk.VBox(False, 7)
        vbox.set_border_width(10)
        frame.add(vbox)

        # "in __ hours __ minutes" group
        hbox = gtk.HBox(False, 5)
        self.in_box = gtk.RadioButton(label='in')
        self.in_box.connect('toggled', self.on_in_at_changed, 'in')
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

        # "at __:__" group
        hbox = gtk.HBox(False, 2)
        self.at_box = gtk.RadioButton(self.in_box, 'at')
        self.at_box.connect('toggled', self.on_in_at_changed, 'at')
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

        # Message entry
        hbox = gtk.HBox(False, 5)
        hbox.pack_start(gtk.Label('Message:'), False)
        self.message = gtk.Entry()
        hbox.pack_start(self.message)
        main_vbox.pack_start(hbox, False)

        # Button
        alignment = gtk.Alignment(1, 0, 0, 0)
        button = gtk.Button(stock=gtk.STOCK_EXECUTE)
        alignment.add(button)
        main_vbox.pack_start(alignment, False)

        return main_vbox

    def on_destroy(self, widget):
        """ Backup results because destroy() might destroy them """
        self.result_time = self.get_time()
        self.result_message = self.get_message()

    def on_in_at_changed(self, widget, groupname):
        """ Allow only one set of widgets to be sensitive """
        if groupname == 'at':
            self.at_hours.set_sensitive(True)
            self.at_minutes.set_sensitive(True)
            self.in_hours.set_sensitive(False)
            self.in_minutes.set_sensitive(False)
        elif groupname == 'in':
            self.in_hours.set_sensitive(True)
            self.in_minutes.set_sensitive(True)
            self.at_hours.set_sensitive(False)
            self.at_minutes.set_sensitive(False)
        else:
            print "Unknown groupname"

    def set_in(self, hours, minutes):
        """ Set "in" group and make it active """
        self.in_box.set_active(False)
        self.in_box.set_active(True)
        self.in_hours.set_value(hours)
        self.in_minutes.set_value(minutes)

    def set_at(self, hours, minutes):
        """ Set "at" group and make it active """
        self.at_box.set_active(True)
        self.at_hours.set_value(hours)
        self.at_minutes.set_value(minutes)

    def set_message(self, message):
        """ Set the final message """
        self.message.set_text(message)

    def get_time(self):
        """ Return result parameter times in format (mode, hours, minutes)

        If the dialog was already destroyed, return cached values. """
        if self.result_time is not None:
            return self.result_time

        if self.in_box.get_active():
            mode = 'in'
            hours = self.in_hours.get_value_as_int()
            minutes = self.in_minutes.get_value_as_int()
        else:
            mode = 'at'
            hours = self.at_hours.get_value_as_int()
            minutes = self.at_minutes.get_value_as_int()

        return mode, hours, minutes

    def get_message(self):
        """ Return the final message

        If the dialog was already destroyed, return cached value. """
        if self.result_message is not None:
            return self.result_message
        else:
            return self.message.get_text()

sw = SettingsWindow()
sw.show_all()

sw.connect('destroy', gtk.main_quit)
gtk.main()

# FIXME handling the button

print sw.get_time()
print "'", sw.get_message(), "'"

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

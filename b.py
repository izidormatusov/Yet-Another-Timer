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
#            on 05.11.2011

import gtk
import glib

class NotificationWindow(gtk.Window):
    """ A window which notifies the user and don't allow to just snooze it. """

    def __init__(self, message, duration=5):
        super(NotificationWindow, self).__init__()

        self.duration = duration

        self.set_border_width(10)
        self.set_title(message)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)

        # Disable close function for a while
        self.connect('delete-event', self.on_close)

        # Request attention
        self.set_keep_above(True)

        # Set minimal size
        self.set_geometry_hints(self, min_width=250)

        vbox = gtk.VBox()
        hbox = gtk.HBox()

        # Icon
        self.image = gtk.image_new_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)
        hbox.pack_start(self.image, False)

        # Message
        message_widget = gtk.Label(message)
        message_widget.set_line_wrap(True)
        hbox.pack_start(message_widget)
        vbox.pack_start(hbox, False)

        # Buttons
        self.buttons = []
        hbox = gtk.HBox(True)

        self.wait_button = gtk.Button()
        self.wait_button.original_label = "Wait"
        hbox.pack_start(self.wait_button)

        button = gtk.Button(label="Done")
        button.connect('clicked', gtk.main_quit)
        hbox.pack_start(button)
        self.buttons.append(button)

        button = gtk.Button(label="Restart")
        button.connect('clicked', gtk.main_quit)
        hbox.pack_start(button)
        self.buttons.append(button)

        # Align them to right bottom
        alignment = gtk.Alignment(1, 1, 0, 0)
        alignment.add(hbox)
        vbox.pack_start(alignment, True, True, 5)

        self.add(vbox)

        glib.idle_add(self.on_tick, True)
        glib.timeout_add_seconds(1, self.on_tick)

    def on_close(self, widget, event):
        """ Allow closing only after duration is gone """
        return self.duration > 0

    def on_tick(self, first_time = False):
        """ Update buttons """
        if first_time:
            for button in self.buttons:
                button.hide()

        # Be anoying and request the focus every time
        self.present()

        if self.duration <= 0:
            self.wait_button.hide()
            for button in self.buttons:
                button.show()

            # Set the last widget to default (activable after enter is pressed)
            button = self.buttons[-1]
            button.set_flags(gtk.CAN_DEFAULT)
            button.grab_default()

            # No more ticking
            return False
        else:
            self.wait_button.set_sensitive(False)
            label = "%s (%d)" % (self.wait_button.original_label, self.duration)
            self.wait_button.set_label(label)
            self.duration -= 1

            # Request another tick
            return not first_time

nw = NotificationWindow('The time is up '*1)
nw.connect('destroy', gtk.main_quit)
nw.show_all()

gtk.main()

print "Done"

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

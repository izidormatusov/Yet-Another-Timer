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
#    Created by Izidor Matušov <izidor.matusov@gmail.com>
#            in year 2011

import sys 
import re

try:
    import pygtk
    pygtk.require("2.0")
except:
    print "This application requires PyGTK 2.0"
    sys.exit(1)

import gtk
import glib
import cairo

from tempfile import NamedTemporaryFile
from datetime import datetime
from datetime import timedelta
from time import time as current_time
from time import sleep
from time import mktime
import os

from math import pi
from math import ceil

try:
    import appindicator
    use_indicator = True
except ImportError:
    use_indicator = False

# For storing configuration
from xdg.BaseDirectory import xdg_config_home
from configobj import ConfigObj

DEFAULT_MESSAGE = 'The time is up!'

class SettingsWindow(gtk.Window):
    """ Allows the user to enter parameters of notification. """

    def __init__(self, conf):
        """ Builds GUI and set default values """
        super(SettingsWindow, self).__init__()

        self.set_border_width(10)
        self.set_title('Yet Another Timer')
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_icon_name('clock')

        gui = self._build_gui()
        self.add(gui)

        self.restore_default(conf)

        # Caching results after destroying window
        self.connect('delete-event', self.on_close)
        self.result = None
        self.result_time = None
        self.result_message = None

    def restore_default(self, conf):
        """ Restore values from configuration """
        def get_int(name, default_value):
            """ Ensures that value is integer """
            try:
                return int(conf.get(name, default_value))
            except ValueError:
                return default_value

        mode = conf.get('mode', 'in')

        self.in_box.set_active(mode == 'in')
        self.at_box.set_active(mode != 'in')
        self.on_in_at_changed(self, mode)

        self.in_hours.set_value(get_int('in_hours', 0))
        self.in_minutes.set_value(get_int('in_minutes', 25))

        now = datetime.now()
        self.at_hours.set_value(get_int('at_hours', now.hour))
        self.at_minutes.set_value(get_int('at_minutes', now.minute))

        self.set_message(conf.get('message', DEFAULT_MESSAGE))

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
        button.connect('clicked', self.on_confirm)
        alignment.add(button)
        main_vbox.pack_start(alignment, False)

        return main_vbox

    def on_confirm(self, widget):
        self.result = 'confirm'

    def on_close(self, widget, param):
        self.result = 'close'

    def run(self):
        self.show_all()

        while self.result is None:
            gtk.main_iteration()

        self.result_time = self.get_time()
        self.result_message = self.get_message()

        self.destroy()

        return self.result == 'confirm'

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

class NotificationWindow(gtk.Window):
    """ A window which notifies the user and don't allow to just snooze it. """

    def __init__(self, message, duration=5):
        super(NotificationWindow, self).__init__()

        self.duration = duration
        self.result = None

        self.set_border_width(10)
        self.set_title(message)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.set_resizable(False)
        self.set_icon_name('clock')

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
        button.connect('clicked', self.on_done)
        hbox.pack_start(button)
        self.buttons.append(button)

        button = gtk.Button(label="Restart")
        button.connect('clicked', self.on_restart)
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
        if self.duration > 0:
            # Do not allow to close
            return True
        else:
            self.result = 'close'

    def on_done(self, widget):
        self.result = 'close'

    def on_restart(self, widget):
        self.result = 'new'

    def run(self):
        self.show_all()

        while self.result is None:
            gtk.main_iteration()

        self.destroy()
        return self.result == 'new'

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

class TimerIcon:
    """ Draws a simple timer icon """

    # Hard-wired colors
    foreground_color = (0.86, 0.87, 0.82)
    background_color = (0.2, 0.2, 0.2)

    def __init__(self, outer_circle=False):
        """ Init file for storing icon

        Outer circle defines if the background circle should draw or not
        """
        self.outer_circle = outer_circle

        self.previous_file = None

    def create_image(self, time, max_time):
        """ Create PixBuf for image """

        width, height = 32, 32
        radius = min(width, height) / 2.0

        progress = float(time) / float(max_time)

        pixmap = gtk.gdk.Pixmap(None, width, height, 24)
        cr = pixmap.cairo_create()

        # Background
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Outer circle
        if self.outer_circle:
            cr.set_source_rgb(*self.background_color)
            cr.arc(width / 2.0, height / 2.0, radius, 0, 2*pi)
            cr.fill()

        # Pie
        cr.arc(width / 2.0, height / 2.0, radius, -0.5 * pi + progress * 2 * pi,  1.5 * pi)
        cr.line_to(width/2.0, height/2.0)
        cr.close_path()
        cr.set_source_rgb(*self.foreground_color)
        cr.set_line_width(1.0)
        cr.fill()

        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
        pixbuf = pixbuf.get_from_drawable(pixmap, pixmap.get_colormap(), 0, 0, 0, 0, width, height)
        pixbuf = pixbuf.add_alpha(True, 0, 0, 0)

        return pixbuf

    def clean_previous_image(self):
        """ Remove previous file if it exists """
        if self.previous_file is not None and os.path.exists(self.previous_file):
            os.remove(self.previous_file)

    def save_image(self, time, max_time):
        """ Save image """

        self.clean_previous_image()

        tmp = NamedTemporaryFile(delete=False)
        filename = tmp.name
        tmp.close()

        pixbuf = self.create_image(time, max_time)
        pixbuf.save(filename, "png")

        self.previous_file = filename
        return self.previous_file

    def __del__(self):
        """ Remove the last file """
        self.clean_previous_image()

class Menu(gtk.Menu):
    def __init__(self, notify_at, restart):
        super(Menu, self).__init__()
        self.notify_at = notify_at

        self.time_item = self.add_item('Rest time')
        self.add_separator()
        self.restart = restart
        self.add_item('Restart', self.on_restart)
        self.add_item('Quit', self.on_quit)

    def add_separator(self):
        item = gtk.SeparatorMenuItem()
        self.append(item)
        item.show()

    def add_item(self, label, callback=None):
        item = gtk.MenuItem(label)
        if callback is not None:
            item.connect("activate", callback)
        item.show()
        self.append(item)
        return item

    def on_restart(self, widget):
        self.restart()

    def on_quit(self, widget):
        """ Just quit the application """
        sys.exit(1)

    def update_time(self, time, max_time):
        if self.notify_at:
            timestamp = current_time() + (max_time - time)*60
            date = datetime.fromtimestamp(timestamp)
            label = 'Notify at %02d:%02d' % (date.hour, date.minute)
        else:
            diff_min = ceil((max_time - time) / 60.0)
            if diff_min > 60:
                hours = diff_min / 60
                minutes = diff_min % 60
                label = "Rest time: %d:%02d" % (hours, minutes)
            else:
                label = "Rest time: %d min" % (diff_min)

        self.time_item.set_label(label)

class AppIndicator:
    """ Shows indicator in Unity """

    def __init__(self, notify_at, restart):
        self.timer_icon = TimerIcon()

        self.ind = appindicator.Indicator("yet-another-timer", "",
            appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)

        self.menu = Menu(notify_at, restart)
        self.ind.set_menu(self.menu)

    def update(self, time, max_time):
        self.menu.update_time(time, max_time)
        filename = self.timer_icon.save_image(time, max_time)
        self.ind.set_icon(filename)

class Timer:
    def __init__(self, mode, duration):
        self.duration = duration
        self.time = 0
        self.result = None
        self.ind = AppIndicator(mode == 'at', self.cancel)
        self.timer_source = None

    def run(self):
        self.on_tick()
        self.timer_source = glib.timeout_add_seconds(1, self.on_tick)
        while self.result is None:
            gtk.main_iteration()
        self.ind = None
        return self.result

    def cancel(self):
        self.result = False
        if self.timer_source is not None:
            glib.source_remove(self.timer_source)

    def on_tick(self):
        print "tick"
        if self.time >= self.duration:
            self.result = True
            return False
        else:
            self.ind.update(self.time, self.duration)
            self.time += 1
            return True

def compute_at_difference(hour, minute):
    now = datetime.now()
    future = datetime.now()

    # We want to get this on the next day
    if future.hour > hour or (future.hour == hour and future.minute > minute):
        future += timedelta(days=1)

    future = future.replace(hour=hour, minute=minute)

    end = mktime(future.timetuple())
    start = mktime(now.timetuple())

    return int((end-start)/60)

def parse_time(unparsed_time):
    """ Return time in minutes """

    unparsed_time = unparsed_time.strip()

    match = re.match(r'^(\d+):(\d+)',  unparsed_time)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        return 'at', hour, minute

    match = re.match(r'^(\d+h|)\s*(\d+m)', unparsed_time)
    if match:
        hours = match.group(1)
        if hours == '':
            hours = 0
        else:
            hours = int(hours[:-1])

        minutes = match.group(2)
        if minutes == '':
            minutes = 0
        else:
            minutes = int(minutes[:-1])

        return 'in', hours, minutes

def main(mode=None, hours=None, minutes=None, message=None):
    skip_settings = mode is not None
    done = False

    # Load configuration
    directory = os.path.join(xdg_config_home, "yet-another-timer")
    if not os.path.exists(directory):
        os.makedirs(directory)
    conf = ConfigObj(os.path.join(directory, "config.conf"))

    while not done:
        if not skip_settings:
            settings = SettingsWindow(conf)

            if mode == 'at':
                settings.set_at(hours, minutes)
            elif mode == 'in':
                settings.set_in(hours, minutes)

            if not settings.run():
                done = True
                continue

            mode, hours, minutes = settings.get_time()
            message = settings.get_message()

        if mode == 'at':
            conf['mode'] = 'at'
            conf['at_hours'] = hours
            conf['at_minutes'] = minutes
            duration = compute_at_difference(hours, minutes)
        else:
            conf['mode'] = 'in'
            conf['in_hours'] = hours
            conf['in_minutes'] = minutes
            duration = hours*60 + minutes

        conf['message'] = message
        conf.write()
        skip_settings = False
        
        timer = Timer(mode, duration)
        timer.run()

        notification = NotificationWindow(message)
        done = not notification.run()

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        mode, hours, minutes = parse_time(sys.argv[1])
        message = " ".join(sys.argv[2:])
        if message.strip() == "":
            message = DEFAULT_MESSAGE
        main(mode, hours, minutes, message)
    else:
        main()

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

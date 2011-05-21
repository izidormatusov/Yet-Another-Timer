#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Izidor Matušov <izidor.matusov@gmail.com>
# Date:   21.05.2011

from time import sleep
import sys
import re

import pygtk
pygtk.require('2.0')
import gtk
import glib
import cairo

from math import pi

class StatusIcon(gtk.StatusIcon):
    """ Shows everything needed """

    def __init__(self, max_time):
        super(StatusIcon, self).__init__()

        self.max_time = max_time
        self.update_icon(0)

    def update(self, time):
        """ Update icon and set tooltip """
        width, height = 32, 32
        radius = min(width, height) / 2.0

        progress = float(time) / float(self.max_time)

        print progress

        pixmap = gtk.gdk.Pixmap(None, width, height, 24)
        cr = pixmap.cairo_create()

        # Background
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # Outer circle
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.arc(width / 2.0, height / 2.0, radius, 0, 2*pi)
        cr.fill()

        # Pie
        cr.arc(width / 2.0, height / 2.0, radius, -0.5 * pi + progress * 2 * pi,  1.5 * pi)
        cr.line_to(width/2.0, height/2.0)
        cr.close_path()
        cr.set_source_rgb(0.4, 0.4, 0.4)
        cr.set_line_width(1.0)
        cr.fill()

        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, width, height)
        pixbuf = pixbuf.get_from_drawable(pixmap, pixmap.get_colormap(), 0, 0, 0, 0, width, height)
        pixbuf = pixbuf.add_alpha(True, 0, 0, 0)


        self.set_from_pixbuf(pixbuf)

        self.set_tooltip("Left %s seconds" % (self.max_time - time))


class TimerApp(gtk.Window):
    """ Simple timer which really shows timer window """

    def __init__(self, wait_time, message):
        super(TimerApp, self).__init__(gtk.WINDOW_TOPLEVEL)

        self.wait_time = wait_time
        self.left_time = wait_time

        self.set_border_width(10)
        self.set_title('Time is up')
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_size_request(250, 100)
        self.connect('destroy', self.destroy, None)

        box = gtk.VBox()
        self.label = gtk.Label(message)
        box.pack_start(self.label)

        button = gtk.Button("Okay")
        button.connect('clicked', self.destroy, None)
        box.pack_start(button, expand=False)

        self.add(box)

        self.status_icon = StatusIcon(wait_time)

    def destroy(self, window, data=None):
        """ Finish application """
        gtk.main_quit()

    def tick(self):
        """ Update status icon or show the window! """

        self.left_time -= 1
        self.status_icon.update_icon(self.wait_time - self.left_time)

        if self.left_time <= 0:
            self.show_all()
            self.set_keep_above(True)
            return False
        else:
            return True

    def run(self):
        """ Runs application """

        glib.timeout_add_seconds(1, self.tick)
        gtk.main()

def parse_time(unparsed_time):
    """ Return time in seconds """

    unparsed_time = unparsed_time.strip()

    number = 0
    i = 0
    while i < len(unparsed_time) and ord('0') <= ord(unparsed_time[i]) <= ord('9'):
        number = 10*number + int(unparsed_time[i])
        i += 1

    scale = unparsed_time[i:]
    if scale in ["", "s"]:
        number *= 1
    elif scale == "m":
        number *= 60

    return number

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        wait_time = parse_time(sys.argv[1])
        message = " ".join(sys.argv[2:])

        w = TimerApp(wait_time, message)
        w.run()
    else:
        print "Usage: %s time message" % sys.argv[0]

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

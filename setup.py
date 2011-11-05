#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is inspirated by http://bazaar.launchpad.net/~rojtberg/teatime/mainline/view/head:/setup.py from TeaTime app
#
# Requires python-distutils-extra package

from distutils.core import setup
from DistUtilsExtra.command import *

setup(
      cmdclass = {"build": build_extra.build_extra,
                  "build_i18n":  build_i18n.build_i18n},

      name = "yet-another-timer",
      version = "1.0",
      description = "Remake of Timer-applet for Unity",
      author = "Izidor Matušov",
      author_email = "izidor.matusov@gmail.com",
      url = "https://github.com/iyonius/Yet-Another-Timer",
      license = "GNU GPL v3",
      scripts = ["yet-another-timer.py"],

      data_files = [("share/applications/", ["yet-another-timer.desktop"])]
)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

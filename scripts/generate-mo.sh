#!/bin/bash
# Generate mo files from po files
#
# Script is taken from Geting Things GNOME! project.

LANGUAGES=$(ls po/*.po | sed 's/po\/\(.*\).po/\1/')

for i in $LANGUAGES; do
    mkdir po/$i/LC_MESSAGES/ --parents
    msgfmt po/$i.po --output-file=po/$i/LC_MESSAGES/yet-another-timer.mo
done

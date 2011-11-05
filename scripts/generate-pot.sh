#!/bin/bash
# Generate pot file
#
# Script is taken from Geting Things GNOME! project.

POTFILE="po/yet-another-timer.pot"
rm ${POTFILE}
touch ${POTFILE}
find GTG/ -iname "*.py" -exec xgettext -j --language=Python --keyword=_ --keyword=N_ --from-code utf-8 --output=${POTFILE} {} \;


#! /usr/bin/env python

# $Progeny$
#
# Copyright 2005 Progeny Linux Systems, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Author: Sam Hart

# Designed as a tool for migrating old hackish rpmstrap suites to smartstrap

import sys

def parse_names(namelist):
    donelist = []

    # Get ready for some magic foo that will
    # probably be bug ridden and horrible
    # Kill this part. Fix it. PLEASE
    # FIXME
    for a in namelist:
        b = ''.join(a.split('.')[0:-(len(a.split('.'))-1)])
        donelist.append(b.split('-')[0:-1])
    return donelist

def process(suite_details):
    a = parse_names(suite_details)
    for name_details in a:
        name_details.reverse()
        tmp_name = name_details.pop()
        name_details.reverse()

        tmp_pkg_name = tmp_name.split(":")
        pkg_name = tmp_pkg_name[1]
        if len(name_details):
            pkg_name = pkg_name + "-" + "-".join(name_details)
        print "'%s'," % pkg_name

def usage():
    print "\nsuite_stripper - strips out version info and other stuff returning just package names"
    print "\nUsage:"
    print "\t\trpmstrap --suite-details suite | suite_stripper.py"
    print "\n\n"

def main():
    suite_details = sys.stdin.readlines()

    process(suite_details)

if __name__ == "__main__":
    main()

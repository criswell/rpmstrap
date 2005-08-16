#! /usr/bin/env python

# rpm-refiner.py
#  Given a pile of RPMs will check dependency closure, will attempt to figure out
# their installation order. This is intended for those times that rpm-solver.py
# fails.
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

import rpm_solver
import getopt
import commands
import sys
import tempfile

def process(rpm_dir, recursive, progress, verbose):
    """ Main process if ran from command line """

    solver = rpm_solver.rpm_solver(progress, verbose)
    solver.init_db(rpm_dir, None, recursive)
    needed, problems = solver.dep_closure()

    if len(needed):
        print "Error! The following packages are needed for dependency closure:\n"
        for pkg in needed:
            print "\t" + str(pkg)

        sys.exit(2)

    if len(problems):
        print "Error! The following problems were encountered:\n"
        for pkg in problems:
            print "\t" + str(pkg)
        sys.exit(2)

    # Okay we do stuff
    ordered = solver.order_solver()
    ordered.reverse()
    tmp_dir = tempfile.mkdtemp()

    i = 0
    allnames=""
    new_order = []
    tmp_order = []
    while len(ordered):
        name = ordered.pop()
        fullname = "%s/%s" % (rpm_dir, name)
        if verbose:
            print "---------\nTrying %s" % fullname
        tmp_order.append(fullname)
        allnames = ""
        for tmp_name in tmp_order:
            allnames = "%s %s" % (allnames, tmp_name)

        cmd = "rpm --install --root %s %s" % (tmp_dir, allnames)
        if verbose > 1:
            print cmd
        (status, output) = commands.getstatusoutput(cmd)
        if verbose > 2:
            print status
            print output
        if not status:
            new_order.append(tmp_order)
            tmp_order = []

    for sub_order in new_order:
        for name in sub_order:
            print ("%d:%s" % (i, name))
        i = i + 1

def usage():
    print "rpm_refiner.py -"
    print "  Given a directory of RPMs, attempt to order their"
    print "installation or determine if they have dependency closure."
    print "This uses rpm_solver.py. Basically, use this when rpm_solver.py"
    print "cannot resolve circular dependencies.\n"
    print "\nUSAGE:"
    print "     rpm_refiner.py [options] <RPM_DIR>"
    print "\nWhere [options] may be one of the following:"
    print "\t-v | --verbose\tBe verbose in processing"
    print "\t-p | --progress\tUse progress bar"
    print "\t-r | --recursive\tScan RPM_DIR recursively"
    print "\n\n"


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vpr", ["verbose", "progress", "recursive"])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    verbose = 0
    progress = 0
    recursive = 0

    if len(sys.argv) < 2:
        usage()
        sys.exit(2)

    rpm_dir = sys.argv[-1]

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = verbose + 1

        if o in ("-p", "--progress"):
            progress = 1

        if o in ("-r", "--recursive"):
            recursive = 1

    if verbose > 1: print "WARNING: Excessive debugging"

    process(rpm_dir,recursive, progress, verbose)

if __name__ == "__main__":
    main()

# vim:set ai et sts=4 sw=4 tw=80:

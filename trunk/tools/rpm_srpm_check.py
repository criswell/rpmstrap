#! /usr/bin/env python

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
# rpm-srpm-check.py
#     Takes a pile of RPMs and a pile of SRPMs and checks to
# ensure every RPM has a corresponding SRPM. Will report those
# RPMs lacking SRPMs and what SRPM it was expecting.
#     When optionally given a URI, will attempt to obtain the
# missing SRPMs from there.
#
# usage:
#    rpm-srpm-check.py <RPM-DIR> <SRPM-DIR>
#
# Author: Sam Hart

import os
import fnmatch
import commands
import getopt
import sys
import getopt
import rpm
import tempfile

rpmts = rpm.TransactionSet(tempfile.mkdtemp())
rpmts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)

def list_files(root, patterns='*', recurse=1, return_folders=0):
    """List all the files in a directory"""

    # Expand patterns from semicolon-separated string to list
    pattern_list = patterns.split(';')

    class Bunch:
        def __init__(self, **kwds): self.__dict__.update(kwds)
    arg = Bunch(recurse=recurse, pattern_list=pattern_list, return_folders=return_folders, results=[])

    def visit(arg, dirname, files):
        # Append to arg.results all relevant files
        for name in files:
            fullname = os.path.normpath(os.path.join(dirname, name))
            if arg.return_folders or os.path.isfile(fullname):
                for pattern in arg.pattern_list:
                    if fnmatch.fnmatch(name, pattern):
                        arg.results.append(fullname)
                        break
        # Block recursion if disallowed
        if not arg.recurse: files[:]=[]

    os.path.walk(root, visit, arg)

    return arg.results

def get_rpm_source_info(rpm_filename):
    """Grab the SRPM information from the RPM file"""

    fdno = os.open(rpm_filename, os.O_RDONLY)
    hdr = rpmts.hdrFromFdno(fdno)
    os.close(fdno)
    return hdr[rpm.RPMTAG_SOURCERPM]

def check_srpms(rpm_dir, srpm_dir, recurse=0, get_from_uri=0, uri="", quiet=0):
    """Given directories for SRPMs and RPMs, check we have SRPMs
       for each RPM"""

    wget_opt = ""
    problematic = ""
    srpm_dir = srpm_dir.rstrip("/")
    if quiet:
        wget_opt = "-q"

    for rpm_file in list_files(rpm_dir, '*.rpm', recurse):
        source_rpm = get_rpm_source_info(rpm_file)
        path = ("%s/%s") % (srpm_dir, source_rpm)
        if not quiet>2:
            print "For " + rpm_file + " checking on " + path
        if not os.path.exists(path):
            if not quiet>1:
                print "RPM FILE: " + rpm_file + " is missing SRPM " + source_rpm
            if get_from_uri:
                if not quiet>2:
                    print "Atempting to get " + source_rpm
                full_url = ("%s/%s") % (uri, source_rpm)
                cmd = ("wget %s -O \"%s\" %s") % (wget_opt, path, full_url)
                if not quiet>1: print cmd
                output = commands.getoutput(cmd)
                if not quiet>1 :print output
                if not os.path.exists(path):
                    if not quiet>1: print "SRPM file could not download!"
                    problematic = problematic + "\t" + source_rpm
                    problematic = problematic + "\t" + full_url
                    problematic = problematic + "\t" + path + " - DOES NOT EXIST!\n"

    if not quiet>1:
        print "SRPMs with troubles:"
        print problematic

def do_usage():
    print "rpm-srpm-check.py -"
    print "  Given a pile of RPMs and a pile of SRPMs, check"
    print "  that every RPM has corresponding SRPM. Reports"
    print "  those RPMs that are missing SRPMs and gives the"
    print "  SRPMs it was expecting to find."
    print "\n\n  When optionally given a URI, will attempt to"
    print "  obtain the missing SRPMs from there."
    print "\nUSAGE:"
    print "     rpm-srpm-check.py [-q[qq]] [-r] [-u URI] <RPMDIR> <SRPMDIR>"
    print "\n-q\tThis option specifies 'quiet'. The number of 'q's"
    print "\t\tindicates how quiet to be (with -qqq being silent)"
    print "\n\n"

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "rqu:", ["recursive","uri="])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    uri = ""
    get_from_uri = 0
    recurse = 0 # At some point, it may be nice to do this recursively
    quiet = 0

    for o, a in opts:
        if o in ("-u", "--uri"):
            get_from_uri = 1
            uri = a

        if o in ("-q", "--q"):
            quiet = quiet + 1

        if o in ("-r", "--recursive"):
            recurse = 1

    if get_from_uri:
        if len(args) == 2:
            check_srpms(args[0], args[1], recurse, get_from_uri, uri, quiet)
    elif len(sys.argv) == 3:
        check_srpms(sys.argv[1], sys.argv[2])
    else:
        do_usage()

if __name__ == "__main__":
    main()

# vim:set ai et sts=4 sw=4 tw=80:

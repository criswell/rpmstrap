#! /usr/bin/env python

# rpm-solver.py
#  Given a pile of RPMs will check dependency closure, will attempt to figure out
# their installation order.
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

import os
import fnmatch
import getopt
import sys
import getopt
import rpm
import traceback
import commands

class progress_bar:
    def __init__(self, prefix="Progress :", prog_char="-", col=60, outnode=sys.stdout):
        self.f = outnode
        self.prog_char = prog_char
        self.col = col
        self.spinner = ["|", "/", "-", "\\"]
        self.spin_count = 0
        self.prefix = prefix

    def set(self, prefix="Progress :"):
        self.prefix = prefix

    def clear(self):
        self.f.write("\r")
        for i in range(0, self.col):
            self.f.write(" ")

        self.f.write("\r")
        self.f.flush()

    def progress(self, percentage):
        """Count must be out of 100%"""

        if percentage > 1.0:
            percentage = 1.0

        self.f.write(("\r%s 0 |") % self.prefix)
        width = self.col - len(("\r%s 0  100 |") % self.prefix) + 1
        count = width * percentage

        i = 1
        while i < count:
            self.f.write(self.prog_char)
            i = i + 1

        if count < width:
            self.f.write(">")
            while i < width:
                self.f.write(" ")
                i = i + 1

        if self.spin_count >= len(self.spinner):
            self.spin_count = 0

        self.f.write(self.spinner[self.spin_count])
        self.spin_count = self.spin_count + 1

        self.f.write(" 100  ")
        self.f.flush()

class rpm_solver:
    def __init__(self, progress=0, verbose=0):
        self.progress = progress
        self.verbose = verbose
        self._initdb = 0
        col = commands.getoutput("echo \"$COLUMNS\"")
        try:
            columns = int(col)
        except:
            columns = 60
        self.pb = progress_bar("rpm_solver :", "-", columns, sys.stderr)


    def init_db(self, rpm_dir, avail_dir=None, recursive=0):
        """ Init the database """

        self.solver_db = self.db(rpm_dir, recursive)
        self.solver_db.populate_db(self.verbose, self.pb, 1, self.progress)

        self.use_avail = 0
        self._initdb = 1

        if avail_dir:
            self.avail_db = self.db(avail_dir, recursive)
            self.avail_db.populate_db(self.verbose, self.pb, 0, self.progress)
            self.use_avail = 1

    def what_provides(self, solver_db, name, version=None):
        """ Given a name and a version, see what provides it """

        for hdr_key in solver_db.rpmdb.keys():
            provides = solver_db.rpmdb[hdr_key][rpm.RPMTAG_PROVIDES]
            if name in provides:
                return hdr_key
            file_list = solver_db.rpmdb[hdr_key][rpm.RPMTAG_FILENAMES]
            if name in file_list:
                return hdr_key

        return None

    def dep_closure(self):
        """ Determine if they have dependency closure """

        needed = []
        problems = []

        if self._initdb:
            missing_deps = self.solver_db.ts.check()
            if len(missing_deps):
                for dep in missing_deps:
                    # XXX FIXME
                    # Okay, we completely ignore the version here, which is
                    # wrong wrong WRONG! We should be smacked.
                    if self.use_avail:
                        package = self.what_provides(self.avail_db, dep[1][0])
                        if package:
                            needed.append(package)
                        else:
                            problems.append("%s needs %s" % (dep[0][0], dep[1][0]))
                    else:
                        package = self.what_provides(self.solver_db, dep[1][0])
                        if package:
                            needed.append(package)
                        else:
                            problems.append("%s needs %s" % (dep[0][0], dep[1][0]))
        else:
            problems.append("Database has not been populated")

        return needed, problems

    def _get_filename_from_hdr(self, pkg_te):
        """ Given a package name, find the filename for it """

        pkg = pkg_te.N()

        for name in self.solver_db.rpmdb.keys():
            if pkg == self.solver_db.rpmdb[name][rpm.RPMTAG_NAME]:
                return name

        return None

    def order_solver(self):
        """ Once the database has been populated, try to solve the order """

        order_pkg = []
        order_filename = []

        self.solver_db.ts.order()
        while 1:
            try:
                order_pkg.append(self.solver_db.ts.next())
            except:
                break

        for pkg in order_pkg:
            order_filename.append(self._get_filename_from_hdr(pkg))

        return order_filename

    class db:
        def __init__(self, rpm_dir=".", recurse=1, ext="*.rpm"):
            self.rpm_dir = rpm_dir
            self.recurse = recurse
            self.rpmdb = {}
            self.ext = ext
            self.ts = rpm.TransactionSet()

        def get_rpmdb_size(self):
            return len(self.rpmdb)

        def populate_db(self, verbose, pb, pop_trans=1, progress=0):
            """ Populate our own DB :-)"""

            self.rpm_filenames = self._list_files()

            i = 0.0
            if progress:
                pb.set("Populate RPMDB :")

            for filename in self.rpm_filenames:
                if verbose: print "rpm_solver.db.populate_db : Adding " + str(filename)
                if progress:
                    i = i + 1.0
                    percent = i / len(self.rpm_filenames)
                    pb.progress(percent)

                self.add(filename, pop_trans)

            if progress:
                pb.clear()

        def add(self, filename, pop_trans=1):
            try:
                fname = filename.split("/")[-1]
            except:
                fname = filename
            fdno = os.open(filename, os.O_RDONLY)
            hdr = self.ts.hdrFromFdno(fdno)
            self.rpmdb[fname] = hdr
            os.close(fdno)
            if pop_trans:
                self.ts.addInstall(hdr,None)

        def _list_files(self):
            """List all the files in a directory"""

            root = self.rpm_dir
            patterns = self.ext
            recurse = self.recurse
            return_folders = 0

            # Expand patterns from semicolon-separated string to list
            pattern_list = patterns.split(';')

            class Bunch:
                def __init__(self, **kwds): self.__dict__.update(kwds)
            arg = Bunch(recurse=recurse, pattern_list=pattern_list, return_folders=return_folders, results=[])

            def visit(arg, dirname, files):
                # Append to arg.results all relevant files
                for name in files:
                    fullname = os.path.normpath(os.path.join(dirname, name))
                    fullname = fullname.rstrip()
                    if arg.return_folders or os.path.isfile(fullname):
                        for pattern in arg.pattern_list:
                            if fnmatch.fnmatch(name, pattern):
                                arg.results.append(fullname)
                                break
                # Block recursion if disallowed
                if not arg.recurse: files[:]=[]

            os.path.walk(root, visit, arg)

            return arg.results

def process(rpm_dir, solve_dir, check_only, recursive, progress, verbose):
    """ Main process if ran from command line """

    solver = rpm_solver(progress, verbose)
    solver.init_db(rpm_dir, solve_dir, recursive)
    needed, problems = solver.dep_closure()

    if len(needed):
        print "Error! The following packages are needed for dependency closure:\n"
        for pkg in needed:
            print "\t" + str(pkg)
    if len(problems):
        print "Error! The following problems were encountered:\n"
        for pkg in problems:
            print "\t" + str(pkg)

    if len(problems) or len(needed):
        sys.exit(2)
    elif check_only:
        print ("The RPMs in %s have dependency closure" % rpm_dir)
    else:
        # Okay we do stuff
        ordered = solver.order_solver()
        i = 0
        for name in ordered:
            print ("%d:%s" % (i, name))
            i = i + 1

def usage():
    print "rpm-solver.py -"
    print "  Given a directory of RPMs, attempt to order their"
    print "installation or determine if they have dependency closure."
    print "\nUSAGE:"
    print "     rpm-solver.py [options] <RPM_DIR>"
    print "\nWhere [options] may be one of the following:"
    print "\t-c | --check\tCheck for dependency closure only"
    print "\t-s | --solve\tUse the pool of rpms specified for solving"
    print "\t-v | --verbose\tBe verbose in processing"
    print "\t-p | --progress\tUse progress bar"
    print "\t-r | --recursive\tScan RPM_DIR recursively"
    print "\n\n"


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vprs:c", ["verbose", "progress", "recursive", "solve=", "check"])
    except getopt.GetoptError:
        # print help information and exit:
        usage()
        sys.exit(2)

    verbose = 0
    progress = 0
    recursive = 0
    solve_dir = None
    check_only = 0

    if len(sys.argv) < 2:
        usage()
        sys.exit(2)

    rpm_dir = sys.argv[-1]

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = 1

        if o in ("-p", "--progress"):
            progress = 1

        if o in ("-r", "--recursive"):
            recursive = 1

        if o in ("-s", "--solve"):
            solve_dir = a

        if o in ("-c", "--check"):
            check_only = 1

    process(rpm_dir, solve_dir, check_only, recursive, progress, verbose)

if __name__ == "__main__":
    main()

# vim:set ai et sts=4 sw=4 tw=80:

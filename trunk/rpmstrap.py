#! /usr/bin/env python

import os
import fnmatch
import commands
import getopt
import sys
import getopt
import urllib

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

# Tiny bit of laziness
def chomp(s):
    if s[-2:] == '\r\n':
        return s[:-2]
    if s[-1:] == '\r' or s[-1:] == '\n':
        return s[:-1]
    return s

def install_rpm(root, rpm, verbose=0):
    """Install an RPM into the chroot"""

    if verbose:
        print ":> install_rpm(" + root + ", " + rpm + ")"
        
    cmd = ("rpm -i --root %s %s") % (root, rpm)
    output = commands.getoutput(cmd)
    if verbose:
        print output

def install_pass(root, rpms, verbose=0):
    """For a given pass, install the RPMs"""

    if verbose:
        print ":> install_pass(" + root + ", [" + str(len(rpms)) + "])"

    for rpm in rpms:
        install_rpm(root, rpm, verbose)

def load_rpm_passfile(passfile, verbose=0):
    """Load and parse a pass file."""

    if verbose:
        print ":> load_rpm_passfile(" + passfile + ")"

    pkglist = []

    f = open(passfile, 'r')
    for line in f:
        (passnum, package) = line.split(":")
        passnum = int(passnum) # Ugly, I know
        pkglist[passnum] = package

    f.close()

    return pkglist

def download_rpm(rpm, storage_dir, url, verbose=0):
    """Download a given rpm"""

    if verbose:
        print ":> download_rpm(" + rpm + ", " + storage_dir + ", " + url + ")"

    f = urllib.urlopen(url)
    for line in f:
        print line
    
#def iterate_install(pkglist, root,

download_rpm("flee", "blee", "ftp://mirrors.xmission.com/fedora/core/2/i386/os/Fedora/RPMS/")
#!/bin/sh

BINDIR=/usr/bin
LIBDIR=/usr/lib/rpmstrap
DOCDIR=/usr/share/doc/rpmstrap-0.5

if [ $# != 0 ] ; then
    while true ; do
        case "$1" in
            -h)
                echo "install.sh"
                echo "----------"
                echo "Run with no arguments to install software"
                echo "Run with '-p' to purge/remove old software"
                exit 0
                ;;
            -p)
                rm -f $BINDIR/rpmstrap
                rm -f $BINDIR/rpm-solver.py
                rm -fr $LIBDIR
                rm -fr $DOCDIR
                echo "rpmstrap purged"
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
fi

# Default is to install

cp -fr rpmstrap $BINDIR/.
cp -fr tools/rpm-solver.py $BINDIR/.
mkdir -p $LIBDIR
cp -fr lib/functions $LIBDIR/.
cp -fr lib/scripts $LIBDIR/.
mkdir -p $DOCDIR
cp -fr lib/*.txt $DOCDIR/.
cp -fr LICENSE $DOCDIR/.
cp -fr README $DOCDIR/.
cp -fr TODO $DOCDIR/.

echo rpmstrap installed

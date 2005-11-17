#!/bin/sh

VERSION=0.5.1

if [ "$BINDIR" = "" ]; then
    BINDIR=$DESTDIR/usr/bin
fi

if [ "$LIBDIR" = "" ]; then
    LIBDIR=$DESTDIR/usr/lib/rpmstrap
fi

if [ "$DOCDIR" = "" ]; then
    DOCDIR=/$DESTDIR/usr/share/doc
fi
DOCDIR=$DOCDIR/rpmstrap-$VERSION

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
                rm -f $BINDIR/rpm_solver.py
                rm -f $BINDIR/rpm_refiner.py
                rm -f $BINDIR/rpm_get-arch.py
                rm -f $BINDIR/rpm_get-update.py
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

mkdir -p $BINDIR
cp -fr rpmstrap $BINDIR/.
mkdir -p $LIBDIR
cp -fr lib/functions $LIBDIR/.
cp -fr lib/scripts $LIBDIR/.
cp -fr tools/ $LIBDIR/.
ln -s $LIBDIR/tools/rpm_solver.py $BINDIR/rpm_solver.py
ln -s $LIBDIR/tools/rpm_refiner.py $BINDIR/rpm_refiner.py
ln -s $LIBDIR/tools/rpm_get-arch.py $BINDIR/rpm_get-arch.py
ln -s $LIBDIR/tools/rpm_get-update.py $BINDIR/rpm_get-update.py
mkdir -p $DOCDIR
cp -fr lib/*.txt $DOCDIR/.
cp -fr LICENSE $DOCDIR/.
cp -fr README $DOCDIR/.
cp -fr TODO $DOCDIR/.
cp -fr CHANGES $DOCDIR/.

echo rpmstrap installed

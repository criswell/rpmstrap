#!/bin/sh

BINDIR=/usr/bin
LIBDIR=/usr/lib/rpmstrap
DOCDIR=/usr/share/doc/rpmstrap-0.5

cp -fr rpmstrap $BINDIR/.
mkdir -p $LIBDIR
cp -fr lib/functions $LIBDIR/.
cp -fr lib/scripts $LIBDIR/.
mkdir -p $DOCDIR
cp -fr lib/*.txt $DOCDIR/.
cp -fr LICENSE $DOCDIR/.

echo rpmstrap installed

This is the repo of the legacy rpmstrap tool.

rpmstrap was a tool we made at [Progeny Linux Systems](https://en.wikipedia.org/wiki/Progeny_Linux_Systems) (circa 2004-ish). It was
intended to be the RPM equivalent of debootstrap. We used it in our creation
of RPM-based custom distros.

Progeny at this time was primarily focused on
making custom Linux distros built to spec for customers. We made and maintained
a whole lot of these. I was in charge of the RPM-based distros we made, and this
tool was what I and [Branden Robinson](https://www.debian.org/vote/2005/platforms/branden) made.

It's crazy legacy at this point. Don't use it. It's kept around for archival
purposes only.

If you're curious why the repo looks the way it does it's because back in 2004
we used the state of the art Subversion for our repos! Later on, I converted it
to Mercurial and hosted it on Bitbucket. Later still, I converted it to git
to host at Github. So the repo is all manner of fucky at this point.

# rpmstrap is still around?!

So one funny thing is that rpmstrap is, technically, still around as of 2019. It
was forked *years* ago (like 2008-ish) and pulled into a bunch of virtualization
technologies and tools. For example, I remember finding a version of it living
in VMWare scripts in 2010-ish, and chunks of it were lifted to power sections of
Xen's RPM suite. It's very likely elsewhere as well.

Of course, by 2019 all this shit has likely evolved so far beyond what rpmstrap
originally was, but it's still kind of cool to think that code I wrote in 2004
still lives in some form 15 years later!

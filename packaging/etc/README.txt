This directory contains helpers for doing reproducible builds with SCons.

To force SCons to propagate SOURCE_DATE_EPOCH from the shell running SCons,
the reproducible_site_init.py file can be installed (as site_init.py)
in any site directory - either in the project itself, or more globally.
See the manpage for default site directories or how to set your own path:
https://scons.org/doc/production/HTML/scons-man.html#opt-site-dir.
This code will make sure SOURCE_DATE_EPOCH is set in the execution
environment, meaning any external commands run by SCons will have it
in their environment.  Any logic in your build system itself will still
need to examine this variable.

The shell script reproducible_install.sh can be used to install the
Python site file in your user site directory ($HOME/.scons/site_scons).
It is careful to not overwrite any existing site_init.py there. This
only works for a POSIX shell.

This supports https://reproducible-builds.org/specs/source-date-epoch/

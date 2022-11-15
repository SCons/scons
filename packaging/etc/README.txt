This directory contains a number of scripts/files useful when building/packageing SCons

To force SCons to propagate SOURCE_DATE_EPOCH from the shell running SCons we're providing
a script to create a ~/.scons/site_scons/site_init.py.
Note that reproducible_install.sh will NOT overwite an existing ~/.scons/site_scons/site_init.py
This supports https://reproducible-builds.org/specs/source-date-epoch/
If you wanted to include this in your build tree you would place in site_scons/site_init.py relative
to your SConstruct.
* reproducible_install.sh
* reproducible_site_init.py
###
### THIS FILE IS NO LONGER USED.  THIS IS THE README FILE FOR THE
### SEPARATE BUILD ENGINE PACKAGE FROM THE ORIGINAL (DRAFT) PACKAGING
### SCHEME.  WE'RE SAVING THIS IN CASE WE NEED OR WANT TO RESURRECT
### A SEPARATE BUILD ENGINE PACKAGE IN THE FUTURE.
###
# __COPYRIGHT__
# __FILE__ __REVISION__ __DATE__ __DEVELOPER__


                 SCons - a software construction tool

                         Version __VERSION__


This is an alpha release of the SCons build engine, a Python extension
module for building software (and other files).  The SCons build engine
manages dependencies and executes commands or Python functions to update
out-of-date files (or other objects).


LATEST VERSION
==============

Before going further, you can check that this package you have is
the latest version by checking the SCons download page at:

        http://www.scons.org/download.html


ABOUT SCONS PACKAGES
====================

The complete SCons system is comprised of three separate packages:

    scons
        The scons script itself, plus the SCons build engine
        installed into an SCons-specific library directory.

    python-scons [THIS PACKAGE]
        The SCons build engine, installed into the standard
        Python library directory.

    scons-script
        Only the scons script itself.

Depending on what you want to do with SCons, you may need to install
additional (or other) packages:

    If you just want to use scons (the script) to build software:

        Do not install this package.  Install the scons package instead,
        which contains a copy of both the script and the build engine.
        You will not need to install any other packages.

    If you do NOT want to use the scons script, but you want to use the
    SCons build engine in other Python software:

        Install this package.  You do not need to install any other
        packages.

    If you want to use the scons script AND you want to use the SCons
    build engine in other Python software:

        Install this package AND the scons package.

        Note that this installs two separate copies of the build engine,
        one (in an SCons-specific library directory) used by the scons
        script itself and one (in the standard Python library) used by
        other software.  This allows you the flexibility to upgrade
        one build engine without affecting the other.

    If you want the scons script and other Python software to use the
    same version of the build engine:

        Install this package AND the scons-script package.


INSTALLATION
============

To install this package, simply run the provided Python-standard setup
script as follows:

        # python setup.py

You should have system installation privileges (that is, "root" or
"Administrator") when running the setup.py script.


DOCUMENTATION
=============

Documentation for SCons is available at:

        http://www.scons.org/doc.html


LICENSING
=========

SCons is distributed under the MIT license, a full copy of which is
available in the LICENSE.txt file. The MIT license is an approved Open
Source license, which means:

        This software is OSI Certified Open Source Software.  OSI
        Certified is a certification mark of the Open Source Initiative.

More information about OSI certifications and Open Source software is
available at:

        http://www.opensource.org/


REPORTING BUGS
==============

You can report bugs either by following the "Tracker - Bugs" link
on the SCons project page:

        http://sourceforge.net/projects/scons/

or by sending mail to the SCons developers mailing list:

        scons-devel@lists.sourceforge.net


MAILING LISTS
=============

A mailing list for users of SCons is available.  You may send
questions or comments to the list at:

        scons-users@lists.sourceforge.net

You may subscribe to the mailing list at:

        http://lists.sourceforge.net/lists/listinfo/scons-users

There is also a low-volume mailing list available for announcements
about SCons.  Subscribe at:

        http://lists.sourceforge.net/lists/listinfo/scons-announce


FOR MORE INFORMATION
====================

Check the SCons web site at:

        http://www.scons.org/


AUTHOR INFO
===========

Steven Knight
knight at baldmt dot com
http://www.baldmt.com/~knight/

With more than a little help from:
        Chad Austin
        Charles Crain
        Steve Leblanc
        Anthony Roach
        Steven Shaw


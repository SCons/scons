# __COPYRIGHT__
# __FILE__ __REVISION__ __DATE__ __DEVELOPER__


                 SCons - a software construction tool

                         Version __VERSION__


This is an alpha release of SCons, a tool for building software (and
other files).  SCons is implemented in Python, and its "configuration
files" are actually Python scripts, allowing you to use the full power
of a real scripting language to solve build problems.  You do not,
however, need to know Python to use SCons effectively.

See the RELEASE.txt file for notes about this specific release,
including known problems.  See the CHANGES.txt file for a list of
changes since the previous release.


LATEST VERSION
==============

Before going further, you can check that this package you have is
the latest version by checking the SCons download page at:

        http://www.scons.org/download.html


EXECUTION REQUIREMENTS
======================

Running SCons requires Python version 1.5.2 or later.  There should be
no other dependencies or requirements to run SCons.  (There is, however,
an additional requirement to *install* SCons from this particular
package; see the next section.)

The default SCons configuration assumes use of the Microsoft Visual C++
compiler suite on WIN32 systems, and assumes a C compiler named 'cc',
a C++ compiler named 'c++', and a Fortran compiler named 'g77' (such
as found in the GNU C compiler suite) on any other type of system.
You may, of course, override these default values by appropriate
configuration of Environment construction variables.


INSTALLATION REQUIREMENTS
=========================

Installing SCons from this package requires the Python distutils
package.  The distutils package was not shipped as a standard part of
Python until Python version 1.6, so if your system is running Python
1.5.2, you may not have distutils installed.  If you are running
Python version 1.6 or later, you should be fine.

NOTE TO RED HAT USERS:  All Red Hat Linux versions as late as 7.3
still ship Python 1.5.2 as the default, so you probably do *not* have
distutils installed, unless you have already done so manually.

In this case, your options are:

    --  (Recommended.)  Install from a pre-packaged SCons package that
        does not require distutils:

            Red Hat Linux       scons-__VERSION__-1.noarch.rpm

            Debian GNU/Linux    scons___VERSION__-1_all.deb
                                (or use apt-get)

            Windows             scons-__VERSION__.win32.exe

    --  (Optional.)  Download the latest distutils package from the
        following URL:

            http://www.python.org/sigs/distutils-sig/download.html

        Install the distutils according to the instructions on the page.
        You can then proceed to the next section to install SCons from
        this package.


INSTALLATION
============

Assuming your system satisfies the installation requirements in the
previous section, install SCons from this package simply by running the
provided Python-standard setup script as follows:

        # python setup.py install

This will install the scons script in the default system script
directory (/usr/bin or C:\Python*\Scripts, for example) and the build
engine in an appropriate SCons library directory (/usr/lib/scons or
C:\Python*\SCons, for example).

You should have system installation privileges (that is, "root" or
"Administrator") when running the setup.py script to install SCons in
the default system directories.

If you don't have system installation privileges, you can use the
--prefix option to specify an alternate installation location, such as
your home directory:

        $ python setup.py install --prefix=$HOME

This will install the scons script itself in $HOME/bin and the
associated library in $HOME/lib/scons


DOCUMENTATION
=============

See the RELEASE.txt file for notes about this specific release,
including known problems.  See the CHANGES.txt file for a list of
changes since the previous release.

The scons.1 man page is included in this package, and contains a section
of small examples for getting started using SCons.

Additional documentation for SCons is available at:

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

With plenty of help from the SCons Development team:
        Chad Austin
        Charles Crain
        Steve Leblanc
        Anthony Roach
        Terrel Shumway


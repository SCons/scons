SCons - a software construction tool
####################################

.. image:: https://img.shields.io/badge/IRC-scons-blue.svg
   :target: http://webchat.freenode.net/?channels=%23scons&uio=d4
   :alt: IRC

.. image:: https://img.shields.io/sourceforge/dm/scons.svg
   :target: https://sourceforge.net/projects/scons
   :alt: Sourceforge Monthly Downloads

.. image:: https://img.shields.io/sourceforge/dt/scons.svg
   :target: https://sourceforge.net/projects/scons
   :alt: Sourceforge Total Downloads

.. image:: https://travis-ci.org/SCons/scons.svg?branch=master
   :target: https://travis-ci.org/SCons/scons
   :alt: Travis CI build status

.. image:: https://ci.appveyor.com/api/projects/status/github/SCons/scons?svg=true&branch=master
   :target: https://ci.appveyor.com/project/SCons/scons
   :alt: AppVeyor CI build Status

.. image:: https://codecov.io/gh/SCons/scons/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/SCons/scons
   :alt: CodeCov Coverage Status


Welcome to the SCons development tree.  The real purpose of this tree is to
package SCons for production distribution in a variety of formats, not just to
hack SCons code.

If all you want to do is install and run SCons, it will be easier for you to
download and install the scons-{version}.tar.gz or scons-{version}.zip package
rather than to work with the packaging logic in this tree.

To the extent that this tree is about building SCons packages, the *full*
development cycle is not just to test the code directly, but to package SCons,
unpack the package, "install" SCons in a test subdirectory, and then to run
the tests against the unpacked and installed software.  This helps eliminate
problems caused by, for example, failure to update the list of files to be
packaged.

For just working on making an individual change to the SCons source, however,
you don't actually need to build or install SCons; you *can* actually edit and
execute SCons in-place.  See the following sections below for more
information:

    `Making Changes`_
        How to edit and execute SCons in-place.

    `Debugging`_
        Tips for debugging problems in SCons.

    `Testing`_
        How to use the automated regression tests.

    `Development Workflow`_
        An example of how to put the edit/execute/test pieces
        together in a reasonable development workflow.


Latest Version
==============

Before going further, you can check that this package you have is the latest
version at the SCons download page:

        http://www.scons.org/pages/download.html


Execution Requirements
======================

Running SCons requires either Python version 2.7.* or Python 3.5 or higher.
There should be no other dependencies or requirements to run SCons.

The default SCons configuration assumes use of the Microsoft Visual C++
compiler suite on WIN32 systems, and assumes a C compiler named 'cc', a C++
compiler named 'c++', and a Fortran compiler named 'g77' (such as found in the
GNU C compiler suite) on any other type of system.  You may, of course,
override these default values by appropriate configuration of Environment
construction variables.

By default, SCons knows how to search for available programming tools on
various systems--see the SCons man page for details.  You may, of course,
override the default SCons choices made by appropriate configuration of
Environment construction variables.


Installation Requirements
=========================

Nothing special.


Executing SCons Without Installing
==================================

You can execute the local SCons directly from the src/ subdirectory by first
setting the SCONS_LIB_DIR environment variable to the local src/engine
subdirectory, and then executing the local src/script/scons.py script to
populate the build/scons/ subdirectory.  You would do this as follows on a
Linux or UNIX system (using sh or a derivative like bash or ksh)::

        $ setenv MYSCONS=`pwd`/src
        $ python $MYSCONS/script/scons.py [arguments]

Or on Windows::

        C:\scons>set MYSCONS=%cd%\src
        C:\scons>python %MYSCONS%\script\scons.py [arguments]

An alternative approach is to skip the above and use::

        $ python bootstrap.py [arguments]

bootstrap.py keeps the src/ subdirectory free of compiled Python (\*.pyc or
\*.pyo) files by copying the necessary SCons files to a local bootstrap/
subdirectory and executing it from there.

You can use the -C option to have SCons change directory to another location
where you already have a build configuration set up::

    $ python bootstrap.py -C /some/other/location [arguments]

For simplicity in the following examples, we will only show the bootstrap.py
approach.


Installation
============

    Note: You don't need to build SCons packages or install SCons if you just
    want to work on developing a patch.  See the sections about `Making
    Changes`_ and `Testing`_ below if you just want to submit a bug fix or
    some new functionality.  See the sections below about `Building Packages`_
    and `Testing Packages`_ if your enhancement involves changing the way in
    which SCons is packaged and/or installed on an end-user system.

Assuming your system satisfies the installation requirements in the previous
section, install SCons from this package by first populating the build/scons/
subdirectory.  (For an easier way to install SCons, without having to populate
this directory, use the scons-{version}.tar.gz or scons-{version}.zip
package.)

Populate build/scons/ using a pre-installed SCons
-------------------------------------------------

If you already have an appropriate version of SCons installed on your system,
populate the build/scons/ directory by running::

        $ scons build/scons

Populate build/scons/ using the SCons source
--------------------------------------------

You can also use this version of SCons to populate its own build directory
by using a supplied bootstrap.py script (see the section above about
`Executing SCons Without Installing`_)::

        $ python bootstrap.py build/scons

Install the built SCons files
-----------------------------

Any of the above commands will populate the build/scons/ directory with the
necessary files and directory structure to use the Python-standard setup
script as follows on Linux or UNIX::

        # cd build/scons
        # python setup.py install

Or on Windows::

        C:\scons\>cd build\scons
        C:\scons\build\scons>python setup.py install

By default, the above commands will do the following:

- Install the version-numbered "scons-3.1.0" and "sconsign-3.0.3" scripts in
  the default system script directory (/usr/bin or C:\\Python\*\\Scripts, for
  example).  This can be disabled by specifying the "--no-version-script"
  option on the command line.

- Install scripts named "scons" and "sconsign" scripts in the default system
  script directory (/usr/bin or C:\\Python\*\\Scripts, for example).  This can be
  disabled by specifying the "--no-scons-script" option on the command line,
  which is useful if you want to install and experiment with a new version
  before making it the default on your system.

  On UNIX or Linux systems, you can have the "scons" and "sconsign" scripts be
  hard links or symbolic links to the "scons-3.0.3" and "sconsign-3.0.3"
  scripts by specifying the "--hardlink-scons" or "--symlink-scons" options on
  the command line.

- Install "scons-3.0.3.bat" and "scons.bat" wrapper scripts in the Python
  prefix directory on Windows (C:\\Python\*, for example).  This can be disabled
  by specifying the "--no-install-bat" option on the command line.

  On UNIX or Linux systems, the "--install-bat" option may be specified to
  have "scons-3.0.3.bat" and "scons.bat" files installed in the default system
  script directory, which is useful if you want to install SCons in a shared
  file system directory that can be used to execute SCons from both UNIX/Linux
  and Windows systems.

- Install the SCons build engine (a Python module) in an appropriate
  version-numbered SCons library directory (/usr/lib/scons-3.0.3 or
  C:\\Python\*\\scons-3.0.3, for example).  See below for more options related to
  installing the build engine library.

- Install the troff-format man pages in an appropriate directory on UNIX or
  Linux systems (/usr/share/man/man1 or /usr/man/man1, for example).  This can
  be disabled by specifying the "--no-install-man" option on the command line.
  The man pages can be installed on Windows systems by specifying the
  "--install-man" option on the command line.

Note that, by default, SCons does not install its build engine library in the
standard Python library directories.  If you want to be able to use the SCons
library modules (the build engine) in other Python scripts, specify the
"--standard-lib" option on the command line, as follows::

        # python setup.py install --standard-lib

This will install the build engine in the standard Python library directory
(/usr/lib/python\*/site-packages or C:\\Python*\\Lib\\site-packages).

Alternatively, you can have SCons install its build engine library in a
hard-coded standalone library directory, instead of the default
version-numbered directory, by specifying the "--standalone-lib" option on the
command line, as follows::

        # python setup.py install --standalone-lib

This is usually not recommended, however.

Note that, to install SCons in any of the above system directories, you should
have system installation privileges (that is, "root" or "Administrator") when
running the setup.py script.  If you don't have system installation
privileges, you can use the --prefix option to specify an alternate
installation location, such as your home directory::

        $ python setup.py install --prefix=$HOME

This will install SCons in the appropriate locations relative to $HOME--that
is, the scons script itself $HOME/bin and the associated library in
$HOME/lib/scons, for example.


Making Changes
==============

Because SCons is implemented in a scripting language, you don't need to build
it in order to make changes and test them.

Virtually all of the SCons functionality exists in the "build engine," the
src/engine/SCons subdirectory hierarchy that contains all of the modules that
make up SCons.  The src/script/scons.py wrapper script exists mainly to find
the appropriate build engine library and then execute it.

In order to make your own changes locally and test them by hand, simply edit
modules in the local src/engine/SCons subdirectory tree and use the local
bootstrap.py script (see the section above about `Executing SCons Without
Installing`_)::

    $ python bootstrap.py [arguments]

If you want to be able to just execute your modified version of SCons from the
command line, you can make it executable and add its directory to your $PATH
like so::

    $ chmod 755 src/script/scons.py
    $ export PATH=$PATH:`pwd`/src/script

You should then be able to run this version of SCons by just typing "scons.py"
at your UNIX or Linux command line.

Note that the regular SCons development process makes heavy use of automated
testing.  See the `Testing`_ and `Development Workflow`_ sections below for more
information about the automated regression tests and how they can be used in a
development cycle to validate that your changes don't break existing
functionality.


Debugging
=========

Python comes with a good interactive debugger.  When debugging changes by hand
(i.e., when not using the automated tests), you can invoke SCons under control
of the Python debugger by specifying the --debug=pdb option::

    $ scons --debug=pdb [arguments]
    > /home/knight/SCons/src/engine/SCons/Script/Main.py(927)_main()
    -> default_warnings = [ SCons.Warnings.CorruptSConsignWarning,
    (Pdb)

Once in the debugger, you can set breakpoints at lines in files in the build
engine modules by providing the path name of the file relative to the
src/engine subdirectory (that is, including the SCons/ as the first directory
component)::

    (Pdb) b SCons/Tool/msvc.py:158

The debugger also supports single stepping, stepping into functions, printing
variables, etc.

Trying to debug problems found by running the automated tests (see the
`Testing`_ section, below) is more difficult, because the test automation
harness re-invokes SCons and captures output. Consequently, there isn't an
easy way to invoke the Python debugger in a useful way on any particular SCons
call within a test script.

The most effective technique for debugging problems that occur during an
automated test is to use the good old tried-and-true technique of adding
statements to print tracing information.  But note that you can't just use
"print" statement, or even "sys.stdout.write()" because those change the
SCons output, and the automated tests usually look for matches of specific
output strings to decide if a given SCons invocations passes the test.

To deal with this, SCons supports a Trace() function that (by default) will
print messages to your console screen ("/dev/tty" on UNIX or Linux, "con" on
Windows).  By adding Trace() calls to the SCons source code::

    def sample_method(self, value):
        from SCons.Debug import Trace
        Trace('called sample_method(%s, %s)\n' % (self, value))

You can then run automated tests that print any arbitrary information you wish
about what's going on inside SCons, without interfering with the test
automation.

The Trace() function can also redirect its output to a file, rather than the
screen::

    def sample_method(self, value):
        from SCons.Debug import Trace
        Trace('called sample_method(%s, %s)\n' % (self, value),
              file='trace.out')

Where the Trace() function sends its output is stateful: once you use the
"file=" argument, all subsequent calls to Trace() send their output to the
same file, until another call with a "file=" argument is reached.


Testing
=======

Tests are run by the runtest.py script in this directory.

There are two types of tests in this package:

1. Unit tests for individual SCons modules live underneath the src/engine/
   subdirectory and are the same base name as the module with "Tests.py"
   appended--for example, the unit test for the Builder.py module is the
   BuilderTests.py script.

2. End-to-end tests of SCons live in the test/ subdirectory.

You may specifically list one or more tests to be run::

        $ python runtest.py src/engine/SCons/BuilderTests.py

        $ python runtest.py test/option-j.py test/Program.py

You also use the -f option to execute just the tests listed in a specified
text file::

        $ cat testlist.txt
        test/option-j.py
        test/Program.py
        $ python runtest.py -f testlist.txt

One test must be listed per line, and any lines that begin with '#' will be
ignored (allowing you, for example, to comment out tests that are currently
passing and then uncomment all of the tests in the file for a final validation
run).

The runtest.py script also takes a -a option that searches the tree for all of
the tests and runs them::

        $ python runtest.py -a

If more than one test is run, the runtest.py script prints a summary of how
many tests passed, failed, or yielded no result, and lists any unsuccessful
tests.

The above invocations all test directly the files underneath the src/
subdirectory, and do not require that a build be performed first.  The
runtest.py script supports additional options to run tests against unpacked
packages in the build/test-\*/ subdirectories.  See the `Testing Packages`_
section below.


Development Workflow
====================

    Caveat: The point of this section isn't to describe one dogmatic workflow.
    Just running the test suite can be time-consuming, and getting a patch to
    pass all of the tests can be more so.  If you're genuinely blocked, it may
    make more sense to submit a patch with a note about which tests still
    fail, and how.  Someone else may be able to take your "initial draft" and
    figure out how to improve it to fix the rest of the tests.  So there's
    plenty of room for use of good judgement.

The various techniques described in the above sections can be combined to
create simple and effective workflows that allow you to validate that patches
you submit to SCons don't break existing functionality and have adequate
testing, thereby increasing the speed with which they can be integrated.

For example, suppose your project's SCons configuration is blocked by an SCons
bug, and you decide you want to fix it and submit the patch.  Here's one
possible way to go about doing that (using UNIX/Linux as the development
platform, Windows users can translate as appropriate)):

- Change to the top of your checked-out SCons tree.

- Confirm that the bug still exists in this version of SCons by using the -C
   option to run the broken build::

      $ python bootstrap.py -C /home/me/broken_project .

- Fix the bug in SCons by editing appropriate module files underneath
  src/engine/SCons.

- Confirm that you've fixed the bug affecting your project::

      $ python bootstrap.py -C /home/me/broken_project .

- Test to see if your fix had any unintended side effects that break existing
  functionality::

      $ python runtest.py -a -o test.log

  Be patient, there are more than 700 test scripts in the whole suite.  If you
  are on UNIX/Linux, you can use::

      $ python runtest.py -a | tee test.log

  instead so you can monitor progress from your terminal.

  If any test scripts fail, they will be listed in a summary at the end of the
  log file.  Some test scripts may also report NO RESULT because (for example)
  your local system is the wrong type or doesn't have some installed utilities
  necessary to run the script.  In general, you can ignore the NO RESULT list.

- Cut-and-paste the list of failed tests into a file::

      $ cat > failed.txt
      test/failed-test-1.py
      test/failed-test-2.py
      test/failed-test-3.py
      ^D
      $

- Now debug the test failures and fix them, either by changing SCons, or by
  making necessary changes to the tests (if, for example, you have a strong
  reason to change functionality, or if you find that the bug really is in the
  test script itself).  After each change, use the runtest.py -f option to
  examine the effects of the change on the subset of tests that originally
  failed::

      $ [edit]
      $ python runtest.py -f failed.txt

  Repeat this until all of the tests that originally failed now pass.

- Now you need to go back and validate that any changes you made while getting
  the tests to pass didn't break the fix you originally put in, and didn't
  introduce any *additional* unintended side effects that broke other tests::

      $ python bootstrap.py -C /home/me/broken_project .
      $ python runtest.py -a -o test.log

  If you find any newly-broken tests, add them to your "failed.txt" file and
  go back to the previous step.

Of course, the above is only one suggested workflow.  In practice, there is a
lot of room for judgment and experience to make things go quicker.  For
example, if you're making a change to just the Java support, you might start
looking for regressions by just running the test/Java/\*.py tests instead of
running all of "runtest.py -a".


Building Packages
=================

We use SCons (version 3.0.3 or later) to build its own packages.  If you
already have an appropriate version of SCons installed on your system, you can
build everything by simply running it::

        $ scons

If you don't have SCons already installed on your
system, you can use the supplied bootstrap.py script (see the section above
about `Executing SCons Without Installing`_)::

        $ python bootstrap.py build/scons

Depending on the utilities installed on your system, any or all of the
following packages will be built::

        build/dist/scons-3.0.5.tar.gz
        build/dist/scons-3.0.5.zip
        build/dist/scons-doc-3.0.5.tar.gz
        build/dist/scons-local-3.0.5.tar.gz
        build/dist/scons-local-3.0.5.zip
        build/dist/scons-src-3.0.5.tar.gz
        build/dist/scons-src-3.0.5.zip

The SConstruct file is supposed to be smart enough to avoid trying to build
packages for which you don't have the proper utilities installed.  For
example, if you don't have Debian packaging tools installed, it should just
not build the .deb package, not fail the build.

If you receive a build error, please report it to the scons-devel mailing list
and open a bug report on the SCons bug tracker.

Note that in addition to creating the above packages, the default build will
also unpack one or more of the packages for testing.


Testing Packages
================

A full build will unpack and/or install any .deb, .rpm., .local.tar.gz,
.local.zip, .src.tar.gz, .src.zip, .tar.gz, and .zip packages into separate
build/test-\*/ subdirectories.  (Of course, if a package was not built on your
system, it should not try to install it.)  The runtest.py script supports a -p
option that will run the specified tests (individually or collectively via
the -a option) against the unpacked build/test-/\* subdirectory::

        $ python runtest.py -p local-tar-gz

        $ python runtest.py -p local-zip

        $ python runtest.py -p src-tar-gz

        $ python runtest.py -p src-zip

        $ python runtest.py -p tar-gz

        $ python runtest.py -p zip

(The canonical invocation is to also use the runtest.py -a option so that all
tests are run against the specified package.)


Contents of this Package
========================

Not guaranteed to be up-to-date (but better than nothing):

bench/
    A subdirectory for benchmarking scripts, used to perform timing tests
    to decide what specific idioms are most efficient for various parts of
    the code base.  We check these in so they're available in case we have
    to revisit any of these decisions in the future.

bin/
    Miscellaneous utilities used in SCons development.  Right now,
    some of the stuff here includes:

    - a script that runs pychecker on our source tree;

    - a script that counts source and test files and numbers of lines in each;

    - a prototype script for capturing sample SCons output in xml files;

    - a script that can profile and time a packaging build of SCons itself;

    - a copy of xml_export, which can retrieve project data from SourceForge;
      and

    - scripts and a Python module for translating the SCons home-brew XML
      documentation tags into DocBook and man page format


bootstrap.py
    Build script for running SCons from the current source code checkout. This
    copies SCons files to bootstrap/ subdirectory, and then executes SCons
    with the supplied command-line arguments.

build/
    This doesn't exist yet if you're looking at a vanilla source tree.  This
    is generated as part of our build process, and it's where, believe it or
    not, we *build* everything.

debian/
    Files needed to construct a Debian package. The contents of this directory
    are dictated by the Debian Policy Manual
    (http://www.debian.org/doc/debian-policy). The package will not be
    accepted into the Debian distribution unless the contents of this
    directory satisfy the relevant Debian policies.

doc/
    SCons documentation.  A variety of things here, in various stages of
    (in)completeness.

gentoo/
    Stuff to generate files for Gentoo Linux.

HOWTO/
    Documentation of SCons administrative procedures (making a change,
    releasing a new version).  Maybe other administrative stuff in the future.

LICENSE
    A copy of the copyright and terms under which SCons is distributed (the
    Open Source Initiative-approved MIT license).

LICENSE-local
    A copy of the copyright and terms under which SCons is distributed for
    inclusion in the scons-local-{version} packages.  This is the same as
    LICENSE with a preamble that specifies the licensing terms are for SCons
    itself, not any other package that includes SCons.

QMTest/
    The Python modules we use for testing, some generic modules originating
    elsewhere and some specific to SCons.

README.rst
    What you're looking at right now.

README-local
    A README file for inclusion in the scons-local-{version} packages.
    Similar to this file, but stripped down and modified for people looking at
    including SCons in their shipped software.

rpm/
    The .spec file for building our RPM packages.

runtest.py
    Script for running SCons tests.  By default, this will run a test against
    the code in the local src/ tree, so you don't have to do a build before
    testing your changes.

SConstruct
    The file describing to SCons how to build the SCons distribution.

    (It has been pointed out that it's hard to find the SCons API in this
    SConstruct file, and that it looks a lot more like a pure Python script
    than a build configuration file.  That's mainly because all of the magick
    we have to perform to deal with all of the different packaging formats
    requires a lot of pure Python manipulation.  In other words, don't look at
    this file for an example of how easy it is to use SCons to build "normal"
    software.)

src/
    Where the actual source code is kept, of course.

test/
    End-to-end tests of the SCons utility itself.  These are separate from the
    individual module unit tests, which live side-by-side with the modules
    under src/.


Documentation
=============

See the src/RELEASE.txt file for notes about this specific release, including
known problems.  See the src/CHANGES.txt file for a list of changes since the
previous release.

The doc/man/scons.1 man page is included in this package, and contains a
section of small examples for getting started using SCons.

Additional documentation for SCons is available at:

        http://www.scons.org/documentation.html


Licensing
=========

SCons is distributed under the MIT license, a full copy of which is available
in the LICENSE file.


Reporting Bugs
==============

The SCons project welcomes bug reports and feature requests.

Please make sure you send email with the problem or feature request to
the SCons users mailing list, which you can join via the link below:

        http://two.pairlist.net/mailman/listinfo/scons-users

Once you have discussed your issue on the users mailing list and the
community has confirmed that it is either a new bug or a duplicate of an
existing bug, then please follow the instructions the community provides
to file a new bug or to add yourself to the CC list for an existing bug

You can explore the list of existing bugs, which may include workarounds
for the problem you've run into on GitHub Issues:

        https://github.com/SCons/scons/issues


Mailing Lists
=============

An active mailing list for developers of SCons is available.  You may
send questions or comments to the list at:

        scons-dev@scons.org

You may subscribe to the developer's mailing list using form on this page:

        http://two.pairlist.net/mailman/listinfo/scons-dev

Subscription to the developer's mailing list is by approval.  In practice, no
one is refused list membership, but we reserve the right to limit membership
in the future and/or weed out lurkers.

There is also a low-volume mailing list available for announcements about
SCons.  Subscribe by sending email to:

        announce-subscribe@scons.tigris.org

There are other mailing lists available for SCons users, for notification of
SCons code changes, and for notification of updated bug reports and project
documents.  Please see our mailing lists page for details.


Donations
=========

If you find SCons helpful, please consider making a donation (of cash,
software, or hardware) to support continued work on the project.  Information
is available at:

        http://www.scons.org/donate.html


For More Information
====================

Check the SCons web site at:

        http://www.scons.org/


Author Info
===========

SCons was originally written by Steven Knight, knight at baldmt dot com.
Since around 2010 it has been maintained by the SCons
development team, co-managed by Bill Deegan and Gary Oberbrunner, with
many contributors, including but not at all limited to:

- Chad Austin
- Dirk Baechle
- Charles Crain
- William Deegan
- Steve Leblanc
- Rob Managan
- Greg Noel
- Gary Oberbrunner
- Anthony Roach
- Greg Spencer
- Tom Tanner
- Anatoly Techtonik
- Christoph Wiedemann
- Russel Winder

\... and many others.

Copyright (c) 2001 - 2019 The SCons Foundation


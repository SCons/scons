SCons - a Software Construction Tool
####################################

.. image:: https://img.shields.io/badge/IRC-scons-blue.svg
   :target: https://web.libera.chat/#scons
   :alt: IRC

.. image:: https://img.shields.io/sourceforge/dm/scons.svg
   :target: https://sourceforge.net/projects/scons
   :alt: Sourceforge Monthly Downloads

.. image:: https://img.shields.io/sourceforge/dt/scons.svg
   :target: https://sourceforge.net/projects/scons
   :alt: Sourceforge Total Downloads

.. image:: https://travis-ci.com/SCons/scons.svg?branch=master
   :target: https://travis-ci.com/SCons/scons
   :alt: Travis CI build status

.. image:: https://ci.appveyor.com/api/projects/status/github/SCons/scons?svg=true&branch=master
   :target: https://ci.appveyor.com/project/SCons/scons
   :alt: AppVeyor CI build Status

.. image:: https://codecov.io/gh/SCons/scons/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/SCons/scons
   :alt: CodeCov Coverage Status

.. image:: https://github.com/SCons/scons/workflows/SCons%20Build/badge.svg
   :target: https://github.com/SCons/scons/actions?query=workflow%3A%22SCons+Build%22
   :alt: Github Actions


What is SCons?
==============

SCons is an Open Source software construction tool which orchestrates the construction of software
(and other tangible products such as documentation files) by determining which
component pieces must be built or rebuilt and invoking the necessary
commands to build them.


Features:

    * Configuration files are Python scripts -
      use the power of a real programming language
      to solve build problems; no complex domain-specific language to learn.
    * Reliable, automatic dependency analysis built-in for C, C++ and Fortran.
      No more "make depend" or "make clean" to get all of the dependencies.
      Dependency analysis is easily extensible through user-defined
      dependency Scanners for other languages or file types.
    * Built-in support for C, C++, D, Java, Fortran, Yacc, Lex, Qt and SWIG,
      and building TeX and LaTeX documents.
      Easily extensible through user-defined Builders for other languages
      or file types.
    * Building from central repositories of source code and/or pre-built targets.
    * Built-in support for Microsoft Visual Studio, including generation of
      .dsp, .dsw, .sln and .vcproj files.
    * Reliable detection of build changes using cryptographic hashes;
      optionally can configure other algorithms including traditional timestamps.
    * Support for parallel builds - can keep multiple jobs running
      simultaneously regardless of directory hierarchy.
    * Integrated Autoconf-like support for finding #include files, libraries,
      functions and typedefs.
    * Global view of all dependencies - no more multiple build passes or
      reordering targets to build everything.
    * Ability to share built files in a cache to speed up multiple builds.
    * Designed from the ground up for cross-platform builds, and known to
      work on Linux, other POSIX systems (including AIX, BSD systems,
      HP/UX, IRIX and Solaris), Windows 7/8/10, MacOS, and OS/2.
    * Written in Python.


Documentation
=============

Documentation for SCons is available at
http://www.scons.org/documentation.html.


Execution Requirements
======================

Running SCons requires Python 3.6 or higher. There should be no other
dependencies or requirements to run standard SCons.
The last release to support Python 3.5 was 4.2.0.

Some experimental features may require additional Python packages
to be installed - at the moment the Ninja feature requires the
supporting `ninja package <https://pypi.org/project/ninja/>`_.

The default SCons configuration assumes use of the Microsoft Visual C++
compiler suite on Win32 systems, and assumes a C compiler named ``cc``, a C++
compiler named ``c++``, and a Fortran compiler named ``gfortran`` (such as found
in the GNU Compiler Collection) on any other type of system.  You may
override these default values by appropriate configuration of variables
in a Construction Environment, or in the case of Cygwin on a Win32 system,
by selecting the 'cygwin' platform, which will set some of those Construction
Variables for you.

By default, SCons knows how to search for available programming tools on
various systems - see the
`SCons man page <https://scons.org/doc/production/HTML/scons-man.html>`_
for details.  You can override
the default SCons choices made by appropriate configuration of
construction variables.


Installation Requirements
=========================

SCons has no installation dependencies beyond a compatible version
of Python. The tools which will be used to to actually construct the
project, such as compilers, documentation production tools, etc.
should of course be installed by the appropriate means.


Getting Started Using SCons
===========================

If you're new to SCons, the first couple of chapters of the
`SCons User Guide <https://scons.org/doc/production/HTML/scons-user.html>`_
provide an excellent starting spot.


Contributing to SCons
=====================

Please see `CONTRIBUTING <https://github.com/scons/scons/CONTRIBUTING.rst>`_.


License
=======

SCons is distributed under the MIT license, a full copy of which is available
in the LICENSE file.


Reporting Bugs
==============

The SCons project welcomes bug reports and feature requests.

Please make sure you send email with the problem or feature request to
the SCons users mailing list, which you can join at
https://two.pairlist.net/mailman/listinfo/scons-users,
or on the SCons Discord server in
`#scons-help <https://discord.gg/bXVpWAy#scons-help>`_.

Once you have discussed your issue on the users mailing list and the
community has confirmed that it is either a new bug or a duplicate of an
existing bug, then please follow the instructions the community provides
to file a new bug or to add yourself to the CC list for an existing bug

You can explore the list of existing bugs, which may include workarounds
for the problem you've run into, on the
`GitHub issue tracker <https://github.com/SCons/scons/issues>`_.


Mailing Lists
=============

In addition to the scons-users list which is appropriate for almost any
question, there is a mailing list specifically for developers of SCons
You may send questions or comments to the list at:

You may subscribe to the developer's mailing list using the form at
https://two.pairlist.net/mailman/listinfo/scons-dev.

Subscription to the developer's mailing list is by approval.  In practice, no
one is refused list membership, but we reserve the right to limit membership
in the future and/or weed out lurkers.

Note that while this list still exists, the number of different places you
can talk about SCons means it is no longer very active.  GitHub has
support for discussions as well as for issues, and there is usually more
immediacy on the Discord chat, so these are probably now considered the
preferred places for "development" topics.


Donations
=========

If you find SCons helpful, please consider making a donation (of cash,
software, or hardware) to support continued work on the project.  Information
is available at https://www.scons.org/donate.html
or the GitHub Sponsors button on https://github.com/scons/scons.


For More Information
====================

Check the SCons web site at https://www.scons.org/


Copyright (c) 2001 - 2024 The SCons Foundation


# __COPYRIGHT__

This directory contains timing configurations for SCons.

Each configuration exists in a subdirectory.  The controlling script
is named TimeSCons-run.py for the configuration.  The TimeSCons-run.py
scripts use TestSCons.TimeSCons, a subclass of TestSCons.TestSCons (both
defined in ../QMTest/TestScons.py), to manage execution of the timing
runs.

Unlike the TestSCons.TestSCons base class, the TestSCons.TimeSCons
subclass copies the contents of its containing directory to the temporary
working directory.  (It avoids copying the .svn directory, and any files
or directories that start with the string "TimeSCons-".)  This allows
the timing configuration files to be checked in directly to our source
code management system, instead of requiring that they be created from
in-line data inside the script.

The simplest-possible TimeSCons-run.py script would look like:

    import TestSCons
    TestSCons.TimeSCons().main()

The above script would end up executing a SConstruct file configuration
in a temporary directory.  The main() method is the standard interface
for a timing run.  See its docstring for precisely what it does.

Although the TestSCons.TimeSCons subclass copies its directory contents to
a temporary working directory for the timing run, because it is a subclass
of TestSCons.TestSCons, it *can* also create files or directories from
in-line data.  This is typically done when it's necessary to create
hundreds of identical input files or directories before running the
timing test, to avoid cluttering our SCM system with hundreds of otherwise
meaningless files.

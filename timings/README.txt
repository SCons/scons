# __COPYRIGHT__

This directory contains timing configurations for SCons.

Each configuration exists in a subdirectory.  The controlling script
is named TimeSCons-run.py for the configuration.  The TimeSCons-run.py
scripts use TestSCons.TimeSCons, a subclass of TestSCons.TestSCons (both
defined in ../testing/framework/TestSCons.py), to manage execution of the
timing runs.

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


STRUCTURE OF A TIMING CONFIGURATION
===================================

A timing configuration should be in a subdirectory and should contain
at least the following three files:

    TimeSCons-run.py

        The script that controls the timing run.  It looks a lot
        like the test scripts (since it uses the same infrastructure)
        except that you instantiate TestSCons.TimeSCons object, not a
        TestSCons.TestSCons object.

        Typically you want to initialize the object with a "variables"
        dict containing one or more parameters whose values control the
        scale of the configuration.  This would typically be the number
        of source files, directories to scan, etc.  The TimeSCons-run.py
        script can then use the value of those variables to generate that
        many copies of input source files, or directories, or what have,
        from in-line data, instead of having to check in a couple hundred
        files for a large configuration.

        These variables get passed to the timed SCons invocation as
        ARGUMENT= arguments on the command line, so the SConstruct
        file can use it to loop through the right number of files /
        directories / what have you.

    SConstruct

        This is the actual SCons configuration that gets tested.  It has
        access to the variable(s) that control the configuration as
        ARGUMENTS from the command line.

        It's possible for the SConstruct file to do additional set up of
        input files and the like, but in general that should be kept to
        a minimum.  We want what the SConscript file does to be dominated
        by the actual execution we're timing, not initialization stuff,
        so most initialization is better left in TimeSCons-run.py.

    config.js

        This gives our buildbot information about the timing configuration
        (specifically, the title) for display.

Note that it's perfectly acceptable to check in additional files that
may be necessary for your configuration.  They'll get copied to the
temporary directory used to run the timing.


RUNNING YOUR TIMING CONFIGURATION
=================================

Because the TimeSCons.py module is a subclass of the whole TestSCons
hierarchy, you use a normal runtest.py invocation to run the timings
configuration:

    $ python runtest.py timings/Configuration/TimeSCons-run.py

This runs the entire timing configuration, which actually runs SCons
itself three times:

    1)  First, with the --help option, to exit immediately after
        reading the SConscript file(s).  This allows us to get a
        rough independent measurement of how much startup cost is
        involved in this configuration, so that the amount can be
        discounted from the

    2)  A full build.

    3)  An rebuild of the full build, which is presumably up-to-date.

When you execute runtest.py from the command line, the  output of
each SCons run is printed on standard output.  (Note this means
that the output can get pretty large if the timing configuration
involves thousands of files.)

The collected memory and time statistics for each run are printed
on standard output, each with the prefix "TRACE:".  These are the
lines that the buildbot grabs to collect the timing statistics for
the graphs available on the web site.


CALIBRATING YOUR TIMING CONFIGURATION
=====================================

One goal we have for timing configurations is that they should take
about 10 seconds to run on our buildbot timing system, which is an older,
slower system than most.

Per above, you presumably defined one or more variables that control the
"size" of your configuration:  the number of input files, directories,
etc.  The timing infrastructure actually reports the value of these
variables in a way that lets us automate the process of adjusting the
variable values to run within a specified amount of time.

The bin/calibrate.py will run your configuration repeatedly, adjusting
the value(s) of the variable(s) that control your configuration until
it gets three successive runs that take between 9.5 and 10.0 seconds
(by default, options let you adjust the range):

    $ python bin/calibrate.py timings/MyNewTimingConfiguration/TimeSCons-run.py
    run   1:   3.124:  TARGET_COUNT=50
    run   2:  11.936:  TARGET_COUNT=160
    run   3:   9.175:  TARGET_COUNT=134
    run   4:  10.489:  TARGET_COUNT=146
    run   5:   9.798:  TARGET_COUNT=139
    run   6:   9.695:  TARGET_COUNT=139
    run   7:   9.670:  TARGET_COUNT=139
    $

If you have multiple variables, it will adjust *all* of the variables
on each run.  In other words, the proportion between your variables will
remain (relatively) constant.

Of course, this needs to be run on a quiet system for the numbers
to converge.  And what you really need to do before committing a
configuration is run bin/calibrate.py on the actual system that runs
our Buildbot timings.  For that, see Bill Deegan or Steven Knight.

Once you have "good" values for your variables, put them in your
TimeSCons-run.py and you should be good to go.  Note that we've started a
convention of also pasting the run output from calibrate.py into comments
in the TimeSCons-run.py, just to preserve some of the historical context
that led to certain values being chosen.


ADDING A NEW TIMING CONFIGURATION
=================================

In addition to creating a subdirectory with at least the pieces listed
above in the "STRUCTURE" section and "CALIBRATING" your variable(s),
you need to update the following file in this directory:

    index.html

        Add an entry to the test_map dictionary for the subdirectory
        you just created.

That should be it before checkin.  After checkin, one of the Buildbot
administrators (currently Bill Deegan or Steven Knight) needs to update
and restart the Buildbot master so that it will start executing the
build step to run the new timing configuration.

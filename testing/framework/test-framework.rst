#######################
SCons Testing Framework
#######################

.. contents::
   :local:

Introduction
============

SCons uses extensive automated tests to ensure quality, so users can
safely upgrade from version to version without any surprise changes in behavior.

Changes to SCons code, whether fix or new feature, need testing support before
being merged. Sometimes this might mean writing tests for an area that didn't
have adequate, or any, testing before. Having tests isn't an
*iron-clad policy*, but exceptions need to be okayed by the core team -
it's good to discuss ahead of time. When in doubt, test it!

This guide should provide enough information to get started. Use it together
with existing tests to "see how it's done".  Note if you're coding in an IDE,
you may need to add the path ``testing/framework`` to the known paths,
or it won't recognize some symbols.


Test organization
=================

There are three categories of SCons tests:

*Unit Tests*
   Unit tests for individual SCons modules live underneath the
   ``SCons/`` subdirectory (that is alongside the code they are testing)
   and use the Python ``unittest`` module to perform assertion-based
   testing of individual routines, classes and methods in the SCons code base.

*End-to-End Tests*
   End-to-end tests of SCons are small self-contained projects that are
   run by calling ``scons`` (or in a few cases, ``sconsign`` or ``scons-time``)
   to execute them, and thus capture the results of
   running all the way through an invocation - end to end.
   They are implemented as Python scripts which are responsible for setup,
   for running the test, and for checking conformance with expectations.
   The tests are runnable standalone but usually executed by the test runner.
   The standard tests are located in the ``test/`` subdirectory,
   and use the test infrastructure modules in the
   ``testing/framework`` subdirectory.

*External Tests*
   For the support of external Tools (in the form of packages, preferably),
   the testing framework can also run in standalone mode.
   You can start it from the top-level directory of your Tool's source tree,
   where it then finds all Python scripts (``*.py``) underneath the local
   ``test/`` directory.  This implies that Tool tests have to be kept in
   a directory named ``test``, like for the SCons core.


Contrasting end-to-end and unit tests
-------------------------------------

End-to-end tests exist to verify hardened parts of the public interface:
features documented in the reference manual that are available
to use in a project. They accomplish this by themselves being
complete (though usually very small) SCons projects.
Unit tests are more for testing internal interfaces which may
not themselves directly have public API guarantees.
They let you hone in on the point of error much more precisely.
As an example, an end-to-end test verifies that
variable contents added by ``env.Append`` actually
appear correctly in issued command lines,
while unit tests verify that internal routine
``SCons.Environment._add_cppdefines`` properly handles the
complexities of combining different types of arguments
and still produce the expected contents of the ``CPPDEFINES``
variable being added to by the ``env.Append`` interface..

If you're pursuing a fix and it can be tested by adding a new
case to a unit test, that is often simpler and more direct.
However, bug reports tend describe end-to-end type behavior
("I put this in my SConscripts, and something went wrong"),
so it's often useful to code an e2e test to match a bug report,
and develop a solution that turns that to a pass.
So pick the testing strategy that makes sense (sometimes both do) -
and if it's possible to reduce an end-to-end test to a unit test, please do

End-to-end tests are by their nature harder to debug. For the unit
tests, you're running a test program directly, so you can drop straight
into the Python debugger by calling ``runtest.py`` with the ``-d / --debug``
option, set some breakpoints and otherwise step through examining
internal state and how it changes as the test is running.
The end-to-end tests are each small SCons projects executed
by an instance of SCons in a subprocess, so the Python debugger is
harder to bring into play in this context.
There's a separate section devoted to debugging ideas:
`Debugging end-to-end tests`_.


Naming conventions
------------------

The unit tests have the same base name as the module to be tested,
with ``Tests`` appended. For packages, it's conventional to put the
test file in the package directory, and there's typically only one test file
for the whole package directory, but feel free to use multiples
if it makes more sense. For example, there's an
``SCons/Platform/PlatformTests.py`` which covers most of the
Platform code, but also ``SCons/Platform/virtualenvTests.py``
for testing the virtualenv (sub-)module.

The end-to-end tests, more or less, follow this naming convention:

* Tests are Python scripts, so they end with a ``.py`` suffix.
* In the *General* form we use

   ``Feature.py``
      for the test of a specified feature; try to keep this name
      reasonably short
   ``Feature-x.py``
      for the test of a specified feature using option ``x``
   ``Feature-live.py``
      for a test which explicitly uses an external tool to operate.
* The *command line option* tests take the form

   ``option-x.py``
      for a lower-case single-letter option
   ``option--X.py``
      upper-case single-letter option (with an extra hyphen, so the
      file names will be unique on case-insensitive systems)
   ``option--lo.py``
      long option; you can abbreviate the long option name to a
      few characters (the abbreviation must be unique, of course).
* Use a suitably named subdirectory if there's a whole group of
   related test files, this allows easier selection.


Testing Architecture
====================

The test framework provides a lot of useful functions for use within a
test program. This includes test setup, parameterization, running tests,
examining results and reporting outcomes. You can run a particular unit test
directly by making sure the Python interpreter can find the framework::

    $ PYTHON_PATH=testing/framework python SCons/ActionTests.py

The framework does *not* provide facilities for test selection,
or otherwise dealing with collections of tests.
For that, SCons provides a runner script ``runtest.py``.
Help is available through the ``-h`` option::

   $ python runtest.py -h

You run tests from the top-level source directory.
To simply run all the tests, use the ``-a`` option::

   $ python runtest.py -a

You may specifically list one or more tests to be run. ``runtest``
considers all arguments it doesn't recognize as options to be
part of the test list::

   $ python runtest.py SCons/BuilderTests.py
   $ python runtest.py -t test/option/option-j.py test/option/option-p.py

Folder names work in the test list as well, so you can do::

   $ python runtest.py test/SWIG

to run all SWIG tests (and no others).

You can also use the ``-f`` option to execute just the tests listed in
a test list file::

   $ cat testlist.txt
   test/option/option-j.py
   test/option/option-p.py
   $ python runtest.py -f testlist.txt

List one test file per line. Lines that begin with the
comment mark ``#`` will be ignored (this lets you quickly change the
test list by commenting out a few tests in the testlist file).

If more than one test is run, the ``runtest.py`` script prints a summary
and count of tests that failed or yielded no result (skips). Skipped
tests do not count towards considering the overall run to have failed,
unless the ``--no-ignore-skips`` option is used. Passed tests can be
listed using the ``--passed`` option, though this tends to make the
result section at the end quite noisy, which is why it's off by default.
Also by default, ``runtest.py`` prints a running count and completion
percentage message for each test case as it finishes, along with the name
of the test file.  You can quiet this output:
have a look at the ``-q``, ``-s`` and ``-k`` options.

Since a test run can produce a lot of output that you may want to examine
later, there is an option ``-o FILE`` to save the same output that went
to the screen to a file named by ``FILE``. There is also an option to
save the results in a custom XML format.

The above invocations all test against the SCons files in the current
directory (that is, in ``./SCons``), and do not require that a packaging
build of SCons be performed first.  This is the most common mode: make
some changes, and test the effects in place.  The ``runtest.py`` script
supports additional options to run tests against unpacked packages in the
``build/test-*/`` subdirectories.

If you are testing a separate Tool outside of the SCons source tree,
call the ``runtest.py`` script in *external* (stand-alone) mode::

   $ python ~/scons/runtest.py -e -a

This ensures that the testing framework doesn't try to access SCons
classes needed for some of the *internal* test cases.

Note that as each test is run, it is executed in a temporary directory
created just for that test, which is by default removed when the
test is complete.  This ensures that your source directories
don't get clobbered with temporary files and changes from the test runs.
If the test itself needs to know the directory, it can be obtained
as ``test.workdir``, or more commonly by calling ``test.workpath()``,
a function which takes a path-component argument and returns the path to
that path-component in the testing directory.

The use of an ephemeral test directory means that you can't simply change
into a directory to debug after a test has gone wrong.
For a way around this, check out the ``PRESERVE`` environment variable.
It can be seen in action in `How to convert old tests to use fixtures`_ below.

Not running tests
=================

If you simply want to check which tests would get executed, you can call
the ``runtest.py`` script with the ``-l`` option combined with whichever
test selection options (see below) you intend to use. Example::

   $ python runtest.py -l test/scons-time

``runtest.py`` also has a ``-n`` option, which prints the command line for
each test which would have been run, but doesn't actually run them::

   $ python runtest.py -n -a

Selecting tests
===============

When started in *standard* mode::

   $ python runtest.py -a

``runtest.py`` assumes that it is run from the SCons top-level source
directory.  It then dives into the ``SCons`` and ``test`` directories,
where it tries to find filenames

``*Test.py``
   for the ``SCons`` directory (unit tests)

``*.py``
   for the ``test`` directory (end-to-end tests)

When using fixtures, you may end up in a situation where you have
supporting Python script files in a subdirectory which shouldn't be
picked up as test scripts of their own.  There are two options here:

   * Add a file with the name ``sconstest.skip`` to your subdirectory. This
     tells ``runtest.py`` to skip the contents of the directory completely.
   * Create a file ``.exclude_tests`` in your subdirectory, and in
     it list line-by-line the files to exclude from testing - the rest
     will still be picked up as long as they meet the selection criteria.

The same rules apply when testing external Tools when using the ``-e``
option.


Example end-to-end test script
==============================

To illustrate how the end-to-end test scripts work, let's walk through
a simple *Hello, world!* example::

    #!python
    import TestSCons

    test = TestSCons.TestSCons()

    test.write('SConstruct', """\
    Program('hello.c')
    """)

    test.write('hello.c', """\
    #include <stdio.h>

    int
    main(int argc, char *argv[])
    {
        printf("Hello, world!\\n");
        exit (0);
    }
    """)

    test.run()

    test.run(program='./hello', stdout="Hello, world!\n")

    test.pass_test()

Line by line explanation of example
-----------------------------------

``import TestSCons``
   Imports the main infrastructure for SCons tests.  This is
   normally the only part of the infrastructure that needs importing.
   If you need Python standard library modules in your code,
   the convention it to import those before the framework.

``test = TestSCons.TestSCons()``
   Initializes an object for testing.  A fair amount happens under
   the covers when the object is created, including:

   * A temporary directory is created for all the in-line files that will
     get created.
   * The temporary directory's removal is arranged for when
     the test is finished.
   * The test does ``os.chdir()`` to the temporary directory.

``test.write('SConstruct', ...)``
   This line creates an ``SConstruct`` file in the temporary directory,
   to be used as input to the ``scons`` run(s) that we're testing.
   Note the use of the Python triple-quoted string for the contents
   of the ``SConstruct`` file (and see the next section for an
   alternative approach).

``test.write('hello.c', ...)``
   This line creates an ``hello.c`` file in the temporary directory.
   Note that we have to escape the newline in the
   ``"Hello, world!\\n"`` string so that it ends up as a single
   backslash in the ``hello.c`` file on disk.

``test.run()``
   This actually runs SCons.  Like the object initialization, things
   happen under the covers:

   * The exit status is verified; the test exits with a failure if
     the exit status is not zero.
   * The error output is examined, and the test exits with a failure
     if there is any.

``test.run(program='./hello', stdout="Hello, world!\n")``
   This shows use of the ``TestSCons.run()`` method to execute a program
   other than ``scons``, in this case the ``hello`` program we just
   built.  The ``stdout=`` keyword argument also tells the
   ``TestSCons.run()`` method to fail if the program output does not
   match the expected string ``"Hello, world!\n"``.  Like the previous
   ``test.run()`` line, it will also fail the test if the exit status is
   non-zero, or there is any error output.

``test.pass_test()``
   This is always the last line in a test script.  If we get to
   this line, it means we haven't bailed out on a failure or skip,
   so the result was good. It prints ``PASSED``
   on the screen and makes sure we exit with a ``0`` status to indicate
   the test passed.  As a side effect of destroying the ``test`` object,
   the created temporary directory will be removed.


Working with fixtures
=====================

In the simple example above, the files to set up the test are created
on the fly by the test program. We give a filename to the ``TestSCons.write()``
method, plus a string holding its contents, and it gets written to the test
directory right before starting.

This simple technique can be seen throughout most of the end-to-end
tests as it was the original technique provided for test developers,
but it is no longer the preferred way to write a new test.
To develop this way, you first need to create the necessary files and
get them to work, then convert them to an embedded string form, which may
involve escaping, using raw strings, and other fiddly details.
These embedded files are then tricky to maintain - they're not
recognized as code by editors, static checkers, or formatters.
Readability is further hurt if the test script grows large -
lots of files-in-strings obscure the flow of the actual testing logic.

In testing parlance, a fixture is a repeatable test setup.  The SCons
test harness allows the use of saved files as well as collections of
files in named directories to be used
in that sense: *the fixture for this test is foo*.  Since these setups can be
reused across multiple tests, the *fixture* terminology applies well.

Note: fixtures must not be treated by SCons as runnable tests. To exclude
them, see instructions in the above section named `Selecting tests`_.

Directory fixtures
------------------

The test method ``dir_fixture(srcdir, [dstdir])``
copies the contents of the specified directory ``srcdir`` from
the directory of the called test script to the current temporary test
directory. The optional ``dstdir`` is
used as a destination path under the temporary working directory.
``dstdir`` is created automatically if it does not already exist.
The ``srcdir`` and ``dstdir`` parameters may each be a list,
which will be concatenated into a path string.

If ``srcdir`` represents an absolute path, it is used as-is.
Otherwise, if the harness was invoked with the environment variable
``FIXTURE_DIRS`` set (which ``runtest.py`` does by default),
the test instance will present that list of directories to search
as ``self.fixture_dirs``. Each of these are additionally searched for
a directory with the name given by ``srcdir``.

A short example showing the syntax::

   test = TestSCons.TestSCons()
   test.dir_fixture('fixture')
   test.run()

This copies all files and subdirectories from the local ``fixture`` directory,
or if not found, from a ``fixture`` located in one of the fixture dirs,
to the temporary directory for the current test, before running the test.

To see an example in action, refer to the test named
``test/packaging/convenience-functions/convenience-functions.py``.


File fixtures
-------------
The test method ``file_fixture(srcfile, dstfile)``
copies the file ``srcfile`` from the directory of the called script
to the temporary test directory.
The optional ``dstfile`` is used as a destination file name
under the temporary working directory, unless it is an absolute path name.
If ``dstfile`` includes directory elements, they are
created automatically if they don't already exist.
The ``srcfile`` and ``dstfile`` parameters may each be a list,
which will be concatenated into a path string.

If ``srcfile`` represents an absolute path, it is used as-is. Otherwise,
any passed in fixture directories are used as additional places to
search for the fixture file, as for the ``dir_fixture`` case.

As an example, with the following code::

   test = TestSCons.TestSCons()
   test.file_fixture('SConstruct')
   test.file_fixture('src/main.cpp', 'src/main.cpp')
   test.run()

The files ``SConstruct`` and ``src/main.cpp`` are copied to the
temporary test directory. Notice the second ``file_fixture`` call
preserves the path of the original, otherwise ``main.cpp``
would have been placed in the top level of the test directory.

Again, a reference example can be found in the current revision
of SCons, see ``test/packaging/sandbox-test/sandbox-test.py``.

For even more examples you should check out one of the external Tools,
e.g. the *Qt5* Tool at
https://github.com/SCons/scons-contrib/tree/master/sconscontrib/SCons/Tool/qt5.
There are many other tools in the contrib repository,
and you can also visit the SCons Tools
Index at https://github.com/SCons/scons/wiki/ToolsIndex for a complete
list of available Tools, though not all may have tests yet.

How to convert old tests to use fixtures
----------------------------------------

Tests using the inline ``TestSCons.write()`` method can fairly easily be
converted to the fixture based approach via a trick: you can capture
the test directory as it is created, which will contain the files
in their final form. To do this, set the environment variable
``PRESERVE`` to a non-zero value when calling ``runtest.py``
to run the test,
and it will preserve the directory rather than getting rid of it,
and report the path.
A thing to keep in mind is some tests rewrite files while
running - for example some tests create an `SConstruct``,
then write a new one for another part of the test,
then possibly do so again - "preserving" will only keep the state
of the test as it exits.  For this and debugging reasons,
it is preferred not to have tests replace the contents of key files
during a run.

So, you should be able to give the commands::

   $ PRESERVE=1 python runtest.py test/packaging/sandbox-test.py

assuming Linux and a bash-like shell. For a Windows ``cmd`` shell, use
``set PRESERVE=1`` (that will leave it set for the duration of the
``cmd`` session, unless manually cleared).

The output will then look something like this::

   1/1 (100.00%) /usr/bin/python test/packaging/sandbox-test.py
   PASSED
   preserved directory /tmp/testcmd.4060.twlYNI

You can copy the files from that directory to your new
*fixture* directory. Then, in the test script you simply remove all the
tedious ``TestSCons.write()`` statements and replace them with a single
``TestSCons.dir_fixture()`` call.

For more complex testing scenarios you can use ``file_fixture`` with
the optional second argument (or the keyword arg ``dstfile``) to assign
a name to the file being copied.  For example, some tests need to
write multiple ``SConstruct`` files across the full run.
These files can be given different names in the source (perhaps using a
suffix to distinguish them), and then be successively copied to the
final name as needed::

   test.file_fixture('fixture/SConstruct.part1', 'SConstruct')
   # more setup, then run test
   test.file_fixture('fixture/SConstruct.part2', 'SConstruct')
   # run new test

As mentioned earlier, this isn't really ideal and it's
preferred in such cases to keep the separate names in the test
directory, and instead vary how the tests are executed, like::

   test.run(arguments=['-f', 'SConstruct.part1'])
   test.run(arguments=['-f', 'SConstruct.part2'])


When not to use a fixture
-------------------------

Static test files are well suited to fixtures, you just copy them over.
Files with dynamically created content - usually to interpolate
information discovered during test setup, are more problematic.
Here's an example of a rather common pattern::

   import TestSCons
   _python_ = TestSCons._python_

   test.write('SConstruct', f"""\
   cc = Environment().Dictionary('CC')
   env = Environment(
       LINK=r'{_python_} mylink.py',
       LINKFLAGS=[],
       CC=r'{_python_} mycc.py',
       CXX=cc,
       CXXFLAGS=[],
   )
   env.Program(target='test1', source='test1.c')
   """

Here the value of ``_python_`` (the path to the Python executable
actually in use for the test) is obtained by the test program from
the framework, and pasted in via f-string formatting in setting up
the string that will make up the contents of the ``SConstruct``.
A simple fixture isn't useful here because the value of ``_python_``
isn't known until runtime (also note that as it will be an
absolute pathname, it is entered using Python raw string notation
to avoid interpretation problems on Windows,
where the path separator is a backslash).

The other files created in this test may still be candidates for
use as fixture files, however.

There's another approach that can be used in this case,
letting you still use a fixture file:
instead of using string interpolation at setup time,
consider passing values at run-time via command-line arguments.
In the example above, you can replace the substitution
of ``_python_`` at file-writing time with a check for a variable
from the command line, and substitute that at run-time,
so instead of the above sequence in the test script,
put this in a new file ``fixture/SConstruct``::

   python = ARGUMENTS.get('PYTHON', 'python')
   cc = Environment().Dictionary('CC')
   env = Environment(
       LINK=rf'{python} mylink.py',
       LINKFLAGS=[],
       CC=rf'{python} mycc.py',
       CXX=cc,
       CXXFLAGS=[],
   )
   env.Program(target='test1', source='test1.c')

Read this in as a file fixture::

   test.file_fixture(srcfile='fixture/SConstruct')

For this to work, you have to supply ``PYTHON`` in the argument list,
so it appears in ``ARGUMENTS`` at run-time::

   test.run(arguments=rf'PYTHON={_python_}')


Debugging end-to-end tests
==========================

An end-to-end tests is a hand-crafted SCons project,
so testing involves building (or cleaning) that project
with suitable arguments to control the behavior.
The tests treat the SCons invocation as a *black box*,
usually looking for *external* effects of the test - targets are
created, generated files have expected contents, files are properly
removed on clean, etc.  They often also look for
the flow of messages from SCons, which is unfortunately a bit fragile
(many a test has been broken by a new Python version changing
the precise format of an exception message, for example).
Some tests do have test code inside the generated files,
and based on the result emit special known strings that
the test can look for.

Simple tricks like inserting ``print`` statements in the SCons code
itself don't really help as they end up disrupting expected output.
For example, ``test.run(stdout="Some text")``
expects a simple string on the standard output stream,
but the presence of a ``print`` in the code means that appears
in the output, too, and the string matching will fail the test.

Even more irritatingly, added text can cause other tests to fail and
obscure the error you're looking for.  Say you have three different
tests in a script exercising different code paths for the same feature,
and the third one is unexpectedly failing. You add some debug prints to
the affected part of SCons, and now the first test of the three starts
failing, aborting the test run before it even gets to the third test -
the one you were trying to debug.

Still, there are some techniques to help debugging.

The first step should be to run the tests so the harness
emits more information, without forcing more information into
the test stdout/stderr which will confuse result evaluation.
``runtest.py`` has several levels of verbosity which can be used
for this purpose::

   $ python runtest.py --verbose=2 test/foo.py

You can also use the internal
``SCons.Debug.Trace()`` function, which prints output to
``/dev/tty`` on Linux/UNIX systems and ``con`` on Windows systems,
so you can see what's going on, but do not contribute to the
captured stdout/stderr and mess up the test expectations.

If you do need to add informational messages in scons code
to debug a problem, you can use logging and send the messages
to a file instead, so they don't interrupt the test expectations.
Or write directly to a trace file of your choosing.

Part of the technique discussed in the section
`How to convert old tests to use fixtures`_ can also be helpful
for debugging purposes.  If you have a failing test, try::

   $ PRESERVE=1 python runtest.py test/failing-test.py

You can now go to the save directory reported from this run and invoke
scons manually (with appropriate arguments matching what the test did)
to see the results without the presence of the test infrastructure which
would otherwise consume output you may be interested in. In this case,
adding debug prints may be more useful.

There are related variables ``PRESERVE_PASS``, ``PRESERVE_FAIL`` and
``PRESERVE_NORESULT`` that preserve the directory only if the test result
was the indicated one, which is helpful if you're trying to work with
multiple tests showing an unusual result.

From a Windows ``cmd`` shell, you will have to set the environment
variable first, it doesn't work on a single line like the example above for
POSIX-style shells.


Test infrastructure
===================

The main end-to-end test API is defined in the ``TestSCons`` class.
``TestSCons`` is a subclass of ``TestCommon``,
which is a subclass of ``TestCmd``.
``TestCmd`` provides facilities for generically "running a command".
``TestCommon`` wraps this with features for result and error handling.
``TestSCons`` specializes that into support for
specifically running the command ``scons``
(there are related classes ``TestSConsign`` for runing ``sconsign``
and ``TestSCons_time`` for running timing tests using ``bin/scons_time.py``.
Those classes are defined in Python files of the same name
in ``testing/framework``.
Start in ``testing/framework/TestCmd.py`` for the base API definitions,
like how to create files (``test.write()``)
and run commands (``test.run()``).

The unit tests do not run a separate instance of SCons, but instead
import the SCons module that they intend to test. Those tests
can usually use the ``TestCmd`` class for testing infrastructure
(temporary directory, file creation, etc.), while the test classes
themselves normally derive from ``unittest.TestCase``.

The match functions work like this:

``TestSCons.match_re``
   match each line with a regular expression.

   * Splits the lines into a list (unless they already are)
   * splits the REs at newlines (unless already a list)
     and puts ``^..$`` around each
   * then each RE must match each line.  This means there must be as many
     REs as lines.

``TestSCons.match_re_dotall``
   match all the lines against a single regular expression.

   * Joins the lines with newline (unless already a string)
   * joins the REs with newline (unless it's a string) and puts ``^..$``
     around the whole  thing
   * then whole thing must match with Python re.DOTALL.

Use them in a test like this::

   test.run(..., match=TestSCons.match_re, ...)

or::

   test.must_match(..., match=TestSCons.match_re, ...)

Often you want to supply arguments to SCons when it is invoked
to run a test, which you can do using an *arguments* parameter::

   test.run(arguments="-O -v FOO=BAR")

One caveat here: the way the parameter is processed is unavoidably
different from typing on the command line - if you need it not to
be split on spaces, pre-split it yourself, and pass the list, like::

   test.run(arguments=["-f", "SConstruct2", "FOO=Two Words"])


Avoiding tests based on tool (non-)existence
============================================

For many tests, if the tool being tested is backed by an external program
which is not installed on the machine under test, it may not be worth
proceeding with the test. For example, it's hard to test compiling code with
a C compiler if no C compiler exists. In this case, the test should be
skipped.

End-to-end
----------

Here's a simple example for end-to-end tests::

   intelc = test.detect_tool('intelc', prog='icpc')
   if not intelc:
       test.skip_test("Could not load 'intelc' Tool; skipping test(s).\n")

See ``testing/framework/TestSCons.py`` for the ``detect_tool()`` method.
It calls the tool's ``generate()`` method, and then looks for the given
program (tool name by default) in ``env['ENV']['PATH']``.

``test.where_is()`` can be used to look for programs that
do not have tool specifications (or you just don't want to
involve a specific tool). The existing test code
will have many samples of using either or both of these to detect
if it is worth even proceeding with a test.

There's an additional consideration for e2e tests: when a project
developer needs a tool that requires some unique setup
(in particular, the path to find an external executable),
they can just adjust their build to make it work in their environment.
It's not practical to change a bunch of tests in the test suite to do a
similar thing. Calling ``test.where_is()`` might return a positive
response based on searching the shell's ``PATH`` environment
variable (which it checks if no specific paths to search are given),
but that does not guarantee the copy of SCons launched to run
the actual testcase will find it, so it may be necessary to
pass the path to the test, perhaps via an argument to ``test.run()``.


Unit Tests
----------

For the unit tests, there are decorators for conditional skipping and
other actions that will produce the correct output display and statistics
in abnormal situations.

``@unittest.skip(reason)``
   Unconditionally skip the decorated test.
   reason should describe why the test is being skipped.

``@unittest.skipIf(condition, reason)``
   Skip the decorated test if condition is true.

``@unittest.skipUnless(condition, reason)``
   Skip the decorated test unless condition is true.

``@unittest.expectedFailure``
   Mark the test as an expected failure.
   If the test fails it will be considered a success.
   If the test passes, it will be considered a failure.

You can also directly call ``testcase.skipTest(reason)``.

Note that it is usually possible to test at least part of the operation of
a tool without the underlying program.  Tools are responsible for setting up
construction variables and having the right builders, scanners and emitters
plumbed into the environment.  These things can be tested by mocking the
behavior of the executable.  Many examples of this can be found in the
``test`` directory. See for example ``test/subdivide.py``.


Testing DOs and DONT'S
======================

We know that needing to write tests makes the job of contributing
code to SCons more cumbersome. But as noted in the introduction,
the testing strategy is extremely important to SCons, it has allowed
the project to serve many users with very few nasty surprises
(won't lie and say there has *never* been a surprise!)
for over two decades. We suggest thinking in terms of test-driven
development for your contribution: you'll need something to show
that your change actually works anyway.  If it's a bug report,
this may be the minimum viable reproducer; if it's a new feature,
you still want to show how something that couldn't be done
before can now be done.  Code that up first, and document your
expectations (for yourself as much as anyone), and use it when
developing the fix/feature.  Often that code can be converted into
a test that will fit into the SCons testuite without doing too
much extra work.  If that work looks too daunting, please ask
for help - tips, advice, and coding help may all be available.


E2E-specific suggestions
------------------------

* **DO** group tests by topic area. This makes selection easier,
  for example the tests specific to the ``yacc`` tool can be run using
  ``runtest.py test/YACC``
* **DO** keep tests simple.  Some tests are by their nature complex,
  but narrowing in on a specific feature makes for easier debugging -
  more simpler test files is easier on future maintainers than a huge
  compilcated one.
* **DON'T** gang too many things together in one file (related to
  the previous item). It's cleaner if
  they're split into different files unless they share complex
  infrastructure. This helps avoid the problem of "fail fast":
  a test aborts when it detects a failure condition,
  and the other tests in the same file don't ever run,
  which may keep you from seeing a pattern exposed
  when several related tests all fail.
* **DON'T** require the use of an external executable "unless necessary".
  Usually the SCons behavior is the thing we want to test,
  not the behavior of the external tool. *Unless necessary* is
  intentionally vague, use your judgement. If it's a ton of work to
  mock an executable's behavior, perhaps in the combinations of
  different flags, don't. However, if you don't actually need the
  output (files or stderr/stdout) of an external, try to avoid.
* **DO** be prepared to skip a test using an external tool
  if it is unavailable. We want the tests to be runnable in many
  configurations, and not produce tons of fails jut because
  that configuration didn't install some things. Yes, we know
  tons of things will fail if you don't have a findable C compiler -
  sorry!
* **DON'T** combine tests that need an external tool with ones that
  do not, split them into separate test files. e2e tests can't do a
  partial skip, so if you successfully complete seven
  of eight tests, and then come to a conditional "skip if tool missing"
  or "skip if on Windows", then the whole test file ends up marked as a skip.
  On the other side, if you have a platform or tool-specific condition
  that does not issue a ``skip_test``, then part of your test may be
  skipped and you'll see no indication of that in the output log.
  Splitting gives you a more complete picture.
* **DO** leave hints when a test requires external executables.
  The current convention is to use the word "live" in the test name,
  either as an ending ( (e.g. ``test/AS/as-live.py``)
  or use it as the entire name of the test (e.g. ``test/SWIG/live.py``).
* **DO** use test fixtures where it makes sense. Real files are easier
  to read than strings embedded in a test script used to create those
  files - not just by humans, but by editors, checkers and formatters.
  And in particular, try to make use of shareable mocked tools, which,
  by getting lots of use, will be better debugged than single-use ones
  (e.g., try to avoid each Fortran test containing its own mock compiler
  ``myfortan.py`` - all those copies will have to be maintained).

Unittest-specific hints
-----------------------

* **DO** test at an appropriate level. A "unit" of SCons behavior is
  something with predictable outcomes, which has multiple consumers.
  A convenience function used by only one other function may not need
  its own tests, as long as the caller is suitably tested.
* **DO** keep tests independent. This is just standard testing practice -
  a test in one function should not depend on the results of an earlier
  test in the same function. Make sure they have independent setup,
  either by repeating the setup, or splitting into a separate function.
* **DO** consider whether "fail fast" is appropriate. Tests within a
  test function can be made independent by using the ``unittest``
  module's ``subTest`` method - if one subtest fails, results will be
  collected and execution continues, which may be more helpful in some
  cases. This is a comparatively recent addition to ``unittest`` (Python
  3.4), so much of SCons' body of unit tests was written without the
  advantage of that feature.
* **DO** make use of helpful ``unittest`` features.  In particular,
  using basic ``assert`` statements leaves you responsible for the output
  if the test fails. Even in simple cases this tends to look awkward.
  The various assert methods, on the other hand, provide decent formatting
  of output on failure, often showing where two complex elements differ,
  and you only need to add something for output if it needs specialization.
  Compare::

    assert out, "expected string", out
    self.assertEqual(out, "expected string")

  There is an assert method for checking that an exception happens
  (``self.assertRaises``), which is more readable than hand-coding something
  with a ``try`` block to check the exception was raised. Please use this!


***********************
SCons Testing Framework
***********************
.. contents::
   :local:

Introduction
============

SCons uses extensive automated tests to ensure quality. The primary goal
is that users be able to upgrade from version to version without
any surprise changes in behavior.

In general, no change goes into SCons unless it has one or more new
or modified tests that demonstrably exercise the bug being fixed or
the feature being added.  There are exceptions to this guideline, but
they should be just that, *exceptions*.  When in doubt, make sure
it's tested.

Test organization
=================

There are three types of SCons tests:

*End-to-End Tests*
   End-to-end tests of SCons are Python scripts (``*.py``) underneath the
   ``test/`` subdirectory.  They use the test infrastructure modules in
   the ``testing/framework`` subdirectory. They build set up complete
   projects and call scons to execute them, checking that the behavior is
   as expected.

*Unit Tests*
   Unit tests for individual SCons modules live underneath the
   ``SCons/`` subdirectory and are the same base name as the module
   to be tested, with ``Tests`` appended  to the basename. For example,
   the unit tests for the ``Builder.py`` module are in the
   ``BuilderTests.py`` script.  Unit tests tend to be based on assertions.

*External Tests*
   For the support of external Tools (in the form of packages, preferably),
   the testing framework is extended so it can run in standalone mode.
   You can start it from the top-level directory of your Tool's source tree,
   where it then finds all Python scripts (``*.py``) underneath the local
   ``test/`` directory.  This implies that Tool tests have to be kept in
   a directory named ``test``, like for the SCons core.


Contrasting end-to-end and unit tests
-------------------------------------

In general, functionality with end-to-end tests
should be considered a hardened part of the public interface (that is,
something that a user might do) and should not be broken.  Unit tests
are now considered more malleable, more for testing internal interfaces
that can change so long as we don't break users' ``SConscript`` files.
(This wasn't always the case, and there's a lot of meaty code in many
of the unit test scripts that does, in fact, capture external interface
behavior.  In general, we should try to move those things to end-to-end
scripts as we find them.)

End-to-end tests are by their nature harder to debug.
You can drop straight into the Python debugger on the unit test
scripts by using the ``runtest.py --pdb`` option, but the end-to-end
tests treat an SCons invocation as a *black box* and just look for
external effects; simple methods like inserting ``print`` statements
in the SCons code itself can disrupt those external effects.
See `Debugging end-to-end tests`_ for some more thoughts.

Naming conventions
------------------

The end-to-end tests, more or less, stick to the following naming
conventions:

#. All tests end with a ``.py`` suffix.
#. In the *General* form we use

   ``Feature.py``
      for the test of a specified feature; try to keep this description
      reasonably short
   ``Feature-x.py``
      for the test of a specified feature using option ``x``
#. The *command line option* tests take the form

   ``option-x.py``
      for a lower-case single-letter option
   ``option--X.py``
      upper-case single-letter option (with an extra hyphen, so the
      file names will be unique on case-insensitive systems)
   ``option--lo.py``
      long option; abbreviate the long option name to a few characters

Running tests
=============

The standard set of SCons tests are run from the top-level source
directory by the ``runtest.py`` script.

Help is available through the ``-h`` option::

   $ python runtest.py -h

To simply run all the tests, use the ``-a`` option::

   $ python runtest.py -a

By default, ``runtest.py`` prints a count and percentage message for each
test case, along with the name of the test file.  If you need the output
to be more silent, have a look at the ``-q``, ``-s`` and ``-k`` options.

You may specifically list one or more tests to be run::

   $ python runtest.py SCons/BuilderTests.py
   $ python runtest.py test/option-j.py test/Program.py

Folder names are allowed in the test list as well, so you can do::

   $ python runtest.py test/SWIG

to run all SWIG tests only.

You can also use the ``-f`` option to execute just the tests listed in
a test list file::

   $ cat testlist.txt
   test/option-j.py
   test/Program.py
   $ python runtest.py -f testlist.txt

One test must be listed per line, and any lines that begin with '#'
will be ignored (the intent being to allow you, for example, to comment
out tests that are currently passing and then uncomment all of the tests
in the file for a final validation run).

If more than one test is run, the ``runtest.py`` script prints a summary
of how many tests passed, failed, or yielded no result, and lists any
unsuccessful tests.

The above invocations all test against the scons files underneath the ``src/``
subdirectory, and do not require that a packaging build of SCons be performed
first.  This is the most common mode: make some changes, and test the
effects in place.
The ``runtest.py`` script supports additional options to run
tests against unpacked packages in the ``build/test-*/`` subdirectories.

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
It can be seen in action in `How to convert old tests to use fixures`_ below.

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
directory.  It then dives into the ``src`` and ``test`` directories,
where it tries to find filenames

``*Test.py``
   for the ``src`` directory (unit tests)

``*.py``
   for the ``test`` directory (end-to-end tests)

When using fixtures, you may end up in a situation where you have
supporting Python script files in a subdirectory which shouldn't be
picked up as test scripts.  There are two options here:

#. Add a file with the name ``sconstest.skip`` to your subdirectory. This
   tells ``runtest.py`` to skip the contents of the directory completely.
#. Create a file ``.exclude_tests`` in each directory in question, and in
   it list line-by-line the files to exclude from testing.

The same rules apply when testing external Tools when using the ``-e``
option.


Example End-to-End test script
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

Explanation
-----------

``import TestSCons``
   Imports the main infrastructure for writing SCons tests.  This is
   normally the only part of the infrastructure that needs importing.
   Sometimes other Python modules are necessary or helpful, and get
   imported before this line.

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
tests as it was the original technique provided to test developers,
but it is no longer the preferred way to write a new test.
To develop this way, you first need to create the necessary files and
get them to work, then convert them to an embedded string form, which may
involve lots of extra escaping.  These embedded files are then tricky
to maintain.  As a test grows multiple steps, it becomes less easy to
read, since many if the embedded strings aren't quite the final files,
and the volume of test code obscures the flow of the testing steps.
Additionally, as SCons moves more to the use of automated code checkers
and formatters to detect problems and keep a standard coding style for
better readability, note that such tools don't look inside strings
for code, so the effect is lost on them.

In testing parlance, a fixture is a repeatable test setup.  The SCons
test harness allows the use of saved files or directories to be used
in that sense: *the fixture for this test is foo*, instead of writing
a whole bunch of strings to create files. Since these setups can be
reusable across multiple tests, the *fixture* terminology applies well.

Note: fixtures must not be treated by SCons as runnable tests. To exclude
them, see instructions in the above section named `Selecting tests`_.

Directory fixtures
------------------

The test harness method ``dir_fixture(srcdir, [dstdir])``
copies the contents of the specified directory ``srcdir`` from
the directory of the called test script to the current temporary test
directory.  The ``srcdir`` name may be a list, in which case the elements
are concatenated into a path first.  The optional ``dstdir`` is
used as a destination path under the temporary working directory.
``distdir`` is created automatically, if it does not already exist.

If ``srcdir`` represents an absolute path, it is used as-is.
Otherwise, if the harness was invoked with the environment variable
``FIXTURE_DIRS`` set (which ``runtest.py`` does by default),
the test instance will present that list of directories to search
as ``self.fixture_dirs``, each of these are additionally searched for
a directory with the name of ``srcdir``.

A short syntax example::

   test = TestSCons.TestSCons()
   test.dir_fixture('image')
   test.run()

would copy all files and subdirectories from the local ``image`` directory
to the temporary directory for the current test, then run it.

To see a real example for this in action, refer to the test named
``test/packaging/convenience-functions/convenience-functions.py``.

File fixtures
-------------

The method ``file_fixture(srcfile, [dstfile])``
copies the file ``srcfile`` from the directory of the called script
to the temporary test directory.
The optional ``dstfile`` is used as a destination file name
under the temporary working directory, unless it is an absolute path name.
If ``dstfile`` includes directory elements, they are
created automatically if they don't already exist.
The ``srcfile`` and ``dstfile`` parameters may each be a list,
which will be concatenated into a path.

If ``srcfile`` represents an absolute path, it is used as-is. Otherwise,
any passed in fixture directories are used as additional places to
search for the fixture file, as for the ``dir_fixture`` case.

With the following code::

   test = TestSCons.TestSCons()
   test.file_fixture('SConstruct')
   test.file_fixture(['src', 'main.cpp'], ['src', 'main.cpp'])
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

How to convert old tests to use fixures
---------------------------------------

Tests using the inline ``TestSCons.write()`` method can fairly easily be
converted to the fixture based approach. For this, we need to get at the
files as they are written to each temporary test directory,
which we can do by taking advantage of an existing debugging aid,
namely that ``runtest.py`` checks for the existence of an environment
variable named ``PRESERVE``. If it is set to a non-zero value, the testing
framework preserves the test directory instead of deleting it, and prints
a message about its name to the screen.

So, you should be able to give the commands::

   $ PRESERVE=1 python runtest.py test/packaging/sandbox-test.py

assuming Linux and a bash-like shell. For a Windows ``cmd`` shell, use
``set PRESERVE=1`` (that will leave it set for the duration of the
``cmd`` session, unless manually cleared).

The output will then look something like this::

   1/1 (100.00%) /usr/bin/python test/packaging/sandbox-test.py
   PASSED
   preserved directory /tmp/testcmd.4060.twlYNI

You can now copy the files from that directory to your new
*fixture* directory. Then, in the test script you simply remove all the
tedious ``TestSCons.write()`` statements and replace them with a single
``TestSCons.dir_fixture()`` call.

For more complex testing scenarios you can use ``file_fixture`` with
the optional second argument (or the keyword arg ``dstfile``) to assign
a name to the file being copied.  For example, some tests need to
write multiple ``SConstruct`` files across the full run.
These files can be given different names in the source (perhaps using a
sufffix to distinguish them), and then be sucessively copied to the
final name as needed::

   test.file_fixture('fixture/SConstruct.part1', 'SConstruct')
   # more setup, then run test
   test.file_fixture('fixture/SConstruct.part2', 'SConstruct')
   # run new test


When not to use a fixture
-------------------------

Note that some files are not appropriate for use in a fixture as-is:
fixture files should be static. If the creation of the file involves
interpolating data discovered during the run of the test script,
that process should stay in the script.  Here is an example of this
kind of usage that does not lend itself to a fixture::

   import TestSCons
   _python_ = TestSCons._python_

   test.write('SConstruct', f"""
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

Here the value of ``_python_`` from the test program is
pasted in via f-string formatting. A fixture would be hard to use
here because we don't know the value of ``_python_`` until runtime
(also note that as it will be a full pathname, it's entered as a
Python rawstring to avoid interpretation problems on Windows,
where the path separator is a backslash).

The other files created in this test may still be candidates for
use as fixture files, however.

Debugging end-to-end tests
==========================

Most of the end to end tests have expectations for standard output
and error embedded in the tests. The expectation could be either
that there is nothing on that stream, or that it will contain
very specific text which the test matches against. So adding
``print()`` calls, or ``sys.stderr.write()`` or similar will
emit data that the tests do not expect, and thus cause further
failures - possibly even obscuring the original error.
Say you have three different tests in a script, and the third
one is unexpectedly failing. You add some debug prints to the
part of scons that is involved, and now the first test of the
three starts failing, aborting the test run before it gets
to the third test you were trying to debug.

Still, there are some techniques to help debugging.

The first step should be to run the tests so the harness
emits more information, without forcing more information into
the test stdout/stderr which will confuse result evaluation.
``runtest.py`` has several verbose levels which can be used
for this purpose::

   $ python runtest.py --verbose=2 test/foo.py

You can also use the internal
``SCons.Debug.Trace()`` function, which prints output to
``/dev/tty`` on Linux/UNIX systems and ``con`` on Windows systems,
so you can see what's going on.

If you do need to add informational messages in scons code
to debug a problem, you can use logging and send the messages
to a file instead, so they don't interrupt the test expectations.

Part of the technique discussed in the section
`How to Convert Old Tests to Use Fixures`_ can also be helpful
for debugging purposes.  If you have a failing test, try::

   $ PRESERVE=1 python runtest.py test/failing-test.py

You can now go to the save directory reported from this run
and invoke the test manually to see what it is doing, without
the presence of the test infrastructure which would otherwise
consume output you may be interested in. In this case,
adding debug prints may be more useful.


Test infrastructure
===================

The main test API is defined in the ``TestSCons`` class.  ``TestSCons``
is a subclass of ``TestCommon``, which is a subclass of ``TestCmd``.
All those classes are defined in Python files of the same name
in ``testing/framework``.
Start in ``testing/framework/TestCmd.py`` for the base API definitions, like how
to create files (``test.write()``) and run commands (``test.run()``).

Use ``TestSCons`` for the end-to-end tests in ``test``, but use
``TestCmd`` for the unit tests in the ``SCons`` directory.

The match functions work like this:

``TestSCons.match_re``
   match each line with an RE

   * Splits the lines into a list (unless they already are)
   * splits the REs at newlines (unless already a list)
     and puts ``^..$`` around each
   * then each RE must match each line.  This means there must be as many
     REs as lines.

``TestSCons.match_re_dotall``
   match all the lines against a single RE

   * Joins the lines with newline (unless already a string)
   * joins the REs with newline (unless it's a string) and puts ``^..$``
     around the whole  thing
   * then whole thing must match with Python re.DOTALL.

Use them in a test like this::

   test.run(..., match=TestSCons.match_re, ...)

or::

   test.must_match(..., match=TestSCons.match_re, ...)

Avoiding tests based on tool existence
======================================

For many tests, if the tool being tested is backed by an external program
which is not installed on the machine under test, it may not be worth
proceeding with the test. For example, it's hard to test complilng code with
a C compiler if no C compiler exists. In this case, the test should be
skipped.

Here's a simple example for end-to-end tests::

   intelc = test.detect_tool('intelc', prog='icpc')
   if not intelc:
       test.skip_test("Could not load 'intelc' Tool; skipping test(s).\n")

See ``testing/framework/TestSCons.py`` for the ``detect_tool()`` method.
It calls the tool's ``generate()`` method, and then looks for the given
program (tool name by default) in ``env['ENV']['PATH']``.

The ``where_is()`` method can be used to look for programs that
are do not have tool specifications. The existing test code
will have many samples of using either or both of these to detect
if it is worth even proceeding with a test.

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

Testing DOs and DONTs
=====================

There's no question that having to write tests in order to get a change
approved - even an apparently trivial change - does make it a little harder
to contribute to the SCons code base - but the requirement to have features
and bugfixes testable is a necessary part of ensuring SCons quality.
Thinking of SCons development in terms of the red/green model from
Test Driven Development should make things a little easier.

If you are working on an SCons bug, try to come up with a simple
reproducer first.  Bug reports (even your own!) are often like *I tried
to do this but it surprisingly failed*, and a reproducer is normally an
``SConstruct`` along with, probably, some supporting files such as source
files, data files, subsidiary SConscripts, etc.  Try to make this example
as simple and clean as possible.  No, this isn't necessarily easy to do,
but winnowing down what triggers a problem and removing the stuff that
doesn't actually contribute to triggering the problem it is a step that
lets you (and later readers) more clearly understand what is going on.
You don't have to turn this into a formal testcase yet, but keep this
reproducer around, and document with it what you expect to happen,
and what actually happens.  This material will help produce an E2E
test later, and this is something you *may* be able to get help with,
if the way the tests are usually written and the test harness proves
too confusing.  With a clean test in hand (make sure it's failing!)
you can go ahead an code up a fix and make sure it passes with the fix
in place.  Jumping straight to a fix without working on a testcase like
this will often lead to a disappointing *how do I come up with a test
so the maintainer will be willing to merge* phase. Asking questions on
a public forum can be productive here.

E2E-specific Suggestions:

* Do not require the use of an external tool unless necessary.
  Usually the SCons behavior is the thing we want to test,
  not the behavior of the external tool. *Necessary* is not a precise term -
  sometimes it would be too time-consuming to write a script to mock
  a compiler with an extensive set of options, and sometimes it's
  not a good idea to assume you know what all those will do vs what
  the real tool does; there may be other good reasons for just going
  ahead and calling the external tool.
* If using an external tool, be prepared to skip the test if it is unavailable.
* Do not combine tests that need an external tool with ones that
  do not - divide these into separate test files. There is no concept
  of partial skip for e2e tests, so if you successfully complete seven
  of eight tests, and then come to a conditional "skip if tool missing"
  or "skip if on Windows", and that branch is taken, then the
  whole test file ends up skipped, and the seven that ran will
  never be recorded.  Some tests follow the convention of creating a
  second test file with the ending ``-live`` for the part that requires
  actually running the external tool.
* In testing, *fail fast* is not always the best policy - if you can think
  of many scenarios that could go wrong and they are all run linearly in
  a single test file, then you only hear about the first one that fails.
  In some cases it may make sense to split them out a bit more, so you
  can see several fails at once, which may show a helpful failure pattern
  you wouldn't spot from a single fail.
* Use test fixtures where it makes sense, and in particular, try to
  make use of shareable mocked tools, which, by getting lots of use,
  will be better debugged (that is, don't have each test produce its
  own ``myfortan.py`` or ``mylex.py`` etc. unless they need drastically
  different behaviors).

Unittest-specific hints:

- Let the ``unittest`` module help!  Lots of the existing tests just
  use a bare ``assert`` call for checks, which works fine, but then
  you are responsible for preparing the message if it fails.  The base
  ``TestCase`` class has methods which know how to display many things,
  for example ``self.assertEqual()`` displays in what way the two arguments
  differ if they are *not* equal. Checking for am expected exception can
  be done with ``self.assertRaises()`` rather than crafting a stub of
  code using a try block for this situation.
- The *fail fast* consideration applies here, too: try not to fail a whole
  testcase on the first problem, if there are more checks to go.
  Again, existing tests may use elaborate tricks for this, but modern
  ``unittest`` has a ``subTest`` context manager that can be used to wrap
  each distinct piece and not abort the testcase for a failing subtest
  (to be fair, this functionality is a recent addition, after most SCons
  unit tests were written - but it should be used going forward).

